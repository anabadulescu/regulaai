import asyncio
from playwright.async_api import async_playwright
import time
from typing import Dict, List, Set, Optional
import json
from urllib.parse import urlparse
import os
import logging
from datetime import datetime
from dark_pattern import classify as classify_dark_pattern
from PIL import Image
import io
from generate_policy import generate_policy
from create_pr import create_pr
import hashlib
from sqlalchemy import create_engine, Table, Column, String, Integer, MetaData
import requests

COOKIE_BANNER_SELECTORS = [
    '[id*="cookie"]',
    '[class*="cookie"]',
    '[id*="consent"]',
    '[class*="consent"]',
    '[id*="gdpr"]',
    '[class*="gdpr"]',
    '[id*="privacy"]',
    '[class*="privacy"]',
    '#cookie-banner',
    '.cookie-banner',
    '#cookie-notice',
    '.cookie-notice',
    '#cookie-consent',
    '.cookie-consent',
    '#gdpr-banner',
    '.gdpr-banner'
]

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/regulaai")
engine = create_engine(DATABASE_URL)
metadata = MetaData()

scan_scripts = Table(
    "scan_scripts", metadata,
    Column("scan_id", String, nullable=False),
    Column("domain", String, nullable=False),
    Column("script_url", String, nullable=False),
    Column("sha256", String, nullable=False),
    Column("response_size", Integer, nullable=False),
)
metadata.create_all(engine)

def log_event(event: str, duration_ms: Optional[int] = None, **kwargs):
    log = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "event": event,
    }
    if duration_ms is not None:
        log["duration_ms"] = str(duration_ms)
    log.update(kwargs)
    logging.info(json.dumps(log))

def load_persona(persona_id: str) -> dict:
    personas_path = os.path.join(os.path.dirname(__file__), 'personas.json')
    with open(personas_path, 'r', encoding='utf-8') as f:
        personas = json.load(f)
    if persona_id not in personas:
        raise ValueError(f"Persona '{persona_id}' not found in personas.json")
    return personas[persona_id]

async def run_scan(url: str, timeout: int = 120000, persona_id: Optional[str] = None, persona: Optional[dict] = None, context=None) -> dict:
    start_time = time.time()
    log_event("scan_started", url=url, persona_id=persona_id)
    if persona_id:
        persona = load_persona(persona_id)
    elif persona is None:
        persona = {}

    context_args = {
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'locale': persona.get('headers', {}).get('Accept-Language', 'en-US'),
        'viewport': persona.get('viewport', {'width': 1280, 'height': 800}),
        'extra_http_headers': persona.get('headers', {}),
    }
    if 'proxy' in persona:
        context_args['proxy'] = persona['proxy']

    if context is None:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(**context_args)
            result = await _run_scan_with_context(context, url, start_time, persona, context_args, timeout, persona_id)
            await context.close()
            await browser.close()
            return result
    else:
        # Reuse provided context
        return await _run_scan_with_context(context, url, start_time, persona, context_args, timeout, persona_id)

async def _run_scan_with_context(context, url, start_time, persona, context_args, timeout, persona_id):
    page = await context.new_page()
    # Accessibility: low-vision (zoom)
    if persona.get('accessibility') == 'low-vision':
        await page.add_init_script("document.body.style.zoom='2'")

    # Capture all network requests
    network_requests = []
    third_party_domains: Set[str] = set()
    main_domain = urlparse(url).netloc

    async def on_request(request):
        req_url = request.url
        network_requests.append(req_url)
        req_domain = urlparse(req_url).netloc
        if req_domain and req_domain != main_domain:
            third_party_domains.add(req_domain)
    page.on("request", on_request)

    scan_id = hashlib.sha256(f"{url}-{time.time()}".encode()).hexdigest()

    try:
        await page.goto(url, wait_until='networkidle', timeout=timeout)
    except Exception as e:
        duration = int((time.time() - start_time) * 1000)
        log_event("scan_failed", duration_ms=duration, url=url, error=str(e), persona_id=persona_id)
        await context.close()
        await page.close()
        raise ValueError(f"Failed to load URL: {url}. Error: {e}")

    # 1. Save full HTML
    html_content = await page.content()
    safe_domain = main_domain.replace(':', '_')
    html_filename = f"scan_{safe_domain}.html"
    with open(html_filename, "w", encoding="utf-8") as f:
        f.write(html_content)

    # 1b. Take screenshot and classify for dark patterns
    screenshot_bytes = await page.screenshot(type="png")
    img = Image.open(io.BytesIO(screenshot_bytes))
    dark_probs = classify_dark_pattern(img)
    violations = []
    for label, prob in dark_probs.items():
        if prob > 0.7:
            violations.append({
                "id": f"dark_{label.lower()}",
                "description": f"Detected dark pattern: {label}",
                "severity": "high",
                "probability": prob
            })

    # 2. Detect <meta name="robots">
    robots_meta = await page.query_selector('meta[name="robots"]')
    robots_content = None
    if robots_meta:
        robots_content = await robots_meta.get_attribute('content')

    # 3. Cookie banner detection (existing)
    cookies = await context.cookies()
    cookie_banner_detected = False
    found_selectors = []
    for selector in COOKIE_BANNER_SELECTORS:
        try:
            element = await page.query_selector(selector)
            if element:
                cookie_banner_detected = True
                found_selectors.append(selector)
        except Exception:
            continue

    # 1c. Capture <script src> hashes and response sizes
    script_hashes = []
    script_elements = await page.query_selector_all('script[src]')
    for script in script_elements:
        src = await script.get_attribute('src')
        if not src:
            continue
        # Absolute URL
        script_url = src if src.startswith('http') else urlparse(url)._replace(path=src).geturl()
        sha256 = hashlib.sha256(script_url.encode()).hexdigest()
        try:
            resp = requests.get(script_url, timeout=5)
            response_size = len(resp.content)
        except Exception:
            response_size = -1
        script_hashes.append({
            "script_url": script_url,
            "sha256": sha256,
            "response_size": response_size
        })
        # Save to DB
        with engine.begin() as conn:
            conn.execute(scan_scripts.insert().values(
                scan_id=scan_id,
                domain=main_domain,
                script_url=script_url,
                sha256=sha256,
                response_size=response_size
            ))

    await page.close()
    scan_time_ms = int((time.time() - start_time) * 1000)
    log_event("scan_completed", duration_ms=scan_time_ms, url=url, persona_id=persona_id)
    return {
        "url": url,
        "cookies": cookies,
        "cookie_banner_detected": cookie_banner_detected,
        "cookie_banner_selectors": found_selectors,
        "scan_time_ms": scan_time_ms,
        "html_file": html_filename,
        "robots_meta": robots_content,
        "network_requests": network_requests,
        "third_party_domains": sorted(list(third_party_domains)),
        "persona_id": persona_id,
        "violations": violations,
        "script_hashes": script_hashes,
        "scan_id": scan_id
    }

def maybe_autofix_privacy_policy(violations, repo_url, company_name, contact_email):
    for v in violations:
        if v.get("id") == "missing_privacy_policy" and os.environ.get("GITHUB_TOKEN"):
            # Generate policy markdown
            policy_md = generate_policy('en', company_name, contact_email)
            # Create PR
            create_pr(
                repo_url=repo_url,
                branch="fix/privacy-policy",
                file_path="docs/privacy.md",
                new_content=policy_md,
                rule_id="missing_privacy_policy"
            )
            break

if __name__ == "__main__":
    import sys
    logging.basicConfig(level=logging.INFO)
    if len(sys.argv) != 2:
        print("Usage: python scan.py <url>")
        sys.exit(1)
    url = sys.argv[1]
    result = asyncio.run(run_scan(url))
    print(json.dumps(result, indent=2)) 