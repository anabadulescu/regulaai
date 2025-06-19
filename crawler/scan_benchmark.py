import asyncio
import time
from statistics import median
from playwright.async_api import async_playwright, BrowserType, BrowserContext
from scan import run_scan

POOL_SIZE = 5  # Number of persistent contexts in the pool
CONCURRENT_SCANS = 25
SCAN_URL = "https://example.com"

class ContextPool:
    def __init__(self, browser_type: BrowserType, user_data_dir_prefix: str, pool_size: int):
        self.browser_type = browser_type
        self.user_data_dir_prefix = user_data_dir_prefix
        self.pool_size = pool_size
        self.contexts = []
        self.lock = asyncio.Lock()
        self.available = asyncio.Queue()

    async def init(self):
        for i in range(self.pool_size):
            context = await self.browser_type.launch_persistent_context(
                user_data_dir=f"{self.user_data_dir_prefix}_{i}", headless=True
            )
            self.contexts.append(context)
            await self.available.put(context)

    async def acquire(self) -> BrowserContext:
        return await self.available.get()

    async def release(self, context: BrowserContext):
        await self.available.put(context)

    async def close(self):
        for ctx in self.contexts:
            await ctx.close()

async def pooled_run_scan(pool: ContextPool, url: str, **kwargs):
    context = await pool.acquire()
    try:
        # Patch run_scan to use the provided context
        # (Assume run_scan can accept a context argument, else you need to refactor run_scan)
        result = await run_scan(url, **kwargs, context=context)
        return result
    finally:
        await pool.release(context)

async def run_benchmark():
    async with async_playwright() as p:
        pool = ContextPool(p.chromium, "./user_data", POOL_SIZE)
        await pool.init()
        durations = []

        async def single_scan_task():
            start = time.time()
            await pooled_run_scan(pool, SCAN_URL)
            end = time.time()
            durations.append((end - start) * 1000)

        tasks = [asyncio.create_task(single_scan_task()) for _ in range(CONCURRENT_SCANS)]
        await asyncio.gather(*tasks)
        await pool.close()
        print(f"Median scan duration for {CONCURRENT_SCANS} concurrent scans: {median(durations):.2f} ms")

if __name__ == "__main__":
    asyncio.run(run_benchmark()) 