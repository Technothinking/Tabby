from playwright.async_api import async_playwright, Browser, BrowserContext
from app.config.settings import settings
import logging
import socket
from urllib.parse import urlparse

logger = logging.getLogger(__name__)

class BrowserDriver:
    def __init__(self):
        self.playwright = None
        self.browser: Browser | None = None
        self.current_context = None
        self.current_page = None
        
    async def connect(self):
        self.playwright = await async_playwright().start()
        
        # Parse CDP URL and resolve hostname to IP to bypass Chrome Host header validation
        url = urlparse(settings.browser_cdp_url)
        try:
            ip = socket.gethostbyname(url.hostname)
            resolved_url = f"{url.scheme}://{ip}:{url.port}{url.path}"
        except Exception:
            resolved_url = settings.browser_cdp_url

        self.browser = await self.playwright.chromium.connect_over_cdp(resolved_url)
        return self.browser

    async def new_context(self) -> BrowserContext:
        if not self.browser:
            await self.connect()
        # Ensure minimum viewport for tests
        self.current_context = await self.browser.new_context(viewport={"width": 1280, "height": 800}) # type: ignore
        return self.current_context

    async def close(self):
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()
