import asyncio
import os
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=[
                "--remote-debugging-port=9222",
                "--remote-debugging-address=0.0.0.0",
                "--no-sandbox"
            ]
        )
        print("Browser CDP server running on 0.0.0.0:9222")
        while True:
            await asyncio.sleep(3600)

if __name__ == "__main__":
    asyncio.run(main())
