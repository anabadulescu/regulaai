import pytest
import asyncio
from scan import run_scan
import http.server, socketserver, threading, time as t
from unittest.mock import patch
from PIL import Image

@pytest.mark.asyncio
async def test_run_scan_404():
    url = "https://httpbin.org/status/404"
    result = await run_scan(url)
    assert result["url"] == url
    assert result["scan_time_ms"] > 0
    assert isinstance(result["cookies"], list)
    assert not result["cookie_banner_detected"]

@pytest.mark.asyncio
async def test_run_scan_delayed_js_cookie_banner(tmp_path):
    html = '''
    <html><head><title>Test</title></head><body>
    <script>
    setTimeout(function() {
      var div = document.createElement('div');
      div.className = 'cookie-banner';
      div.innerText = 'We use cookies!';
      document.body.appendChild(div);
    }, 1000);
    </script>
    </body></html>
    '''
    file = tmp_path / "delayed.html"
    file.write_text(html)
    Handler = http.server.SimpleHTTPRequestHandler
    httpd = socketserver.TCPServer(("", 8001), Handler)
    thread = threading.Thread(target=httpd.serve_forever)
    thread.daemon = True
    thread.start()
    try:
        url = f"http://localhost:8001/{file.name}"
        result = await run_scan(url, timeout=5000)
        assert result["url"] == url
        assert result["cookie_banner_detected"]
        assert any('cookie-banner' in sel for sel in result["cookie_banner_selectors"])
    finally:
        httpd.shutdown()
        thread.join()

@pytest.mark.asyncio
async def test_run_scan_non_http_url():
    with pytest.raises(ValueError):
        await run_scan("ftp://example.com")
    with pytest.raises(ValueError):
        await run_scan("file:///etc/passwd")

@pytest.mark.asyncio
async def test_dark_pattern_violation(monkeypatch, tmp_path):
    def fake_classify(img):
        return {"Confirmshaming": 0.95, "Misdirection": 0.02, "Sneaking": 0.03}
    with patch("dark_pattern.classify", fake_classify):
        html = "<html><body><h1>Test</h1></body></html>"
        file = tmp_path / "test.html"
        file.write_text(html)
        url = f"file://{file}"
        result = await run_scan(url)
        violations = result.get("violations", [])
        assert any(v["id"] == "dark_confirmshaming" for v in violations) 