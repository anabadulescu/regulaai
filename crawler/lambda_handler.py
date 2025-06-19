import json
import asyncio
from scan import run_scan
try:
    from playwright_aws_lambda import chromium  # type: ignore[import]
except ImportError:
    chromium = None  # type: ignore
    from playwright.async_api import async_playwright

async def get_context():
    if chromium is not None:
        return chromium.launch_persistent_context('/tmp/playwright', headless=True)
    else:
        p = await async_playwright().start()
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        return context

def lambda_handler(event, context):
    url = event.get('url')
    if not url:
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'Missing url'})
        }
    loop = asyncio.get_event_loop()
    ctx = loop.run_until_complete(get_context())
    result = loop.run_until_complete(run_scan(url, context=ctx))
    return {
        'statusCode': 200,
        'body': json.dumps(result)
    } 