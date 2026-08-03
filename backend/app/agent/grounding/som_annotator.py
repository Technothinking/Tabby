from playwright.async_api import Page
import base64

SOM_INJECTION_SCRIPT = """
() => {
    // Container for our markers to easily remove them later
    const container = document.createElement('div');
    container.id = 'aboa-som-overlay-container';
    container.style.position = 'fixed';
    container.style.top = '0';
    container.style.left = '0';
    container.style.width = '100vw';
    container.style.height = '100vh';
    container.style.pointerEvents = 'none'; // Critical so they don't block clicks!
    container.style.zIndex = '2147483647'; // Max z-index
    
    const elements = document.querySelectorAll('[data-aboa-id]');
    
    elements.forEach(el => {
        const aboaId = el.getAttribute('data-aboa-id');
        const rect = el.getBoundingClientRect();
        
        // Skip elements completely outside viewport or with 0 bounds
        if (rect.width === 0 || rect.height === 0 || rect.bottom < 0 || rect.right < 0 || rect.top > window.innerHeight || rect.left > window.innerWidth) {
            return;
        }
        
        // Draw Number Label
        const label = document.createElement('div');
        const numPattern = aboaId.match(/\\d+/);
        const num = numPattern ? numPattern[0] : aboaId;
        
        label.textContent = num;
        label.style.position = 'absolute';
        label.style.top = Math.max(0, rect.top - 2) + 'px';
        label.style.left = Math.max(0, rect.left - 2) + 'px';
        label.style.background = '#FF0055';
        label.style.color = '#FFFFFF';
        label.style.fontSize = '12px';
        label.style.fontWeight = 'bold';
        label.style.padding = '2px 4px';
        label.style.borderRadius = '3px';
        label.style.border = '1px solid white';
        label.style.boxShadow = '0px 0px 3px rgba(0,0,0,0.5)';
        
        // Draw Bounding Box
        const box = document.createElement('div');
        box.style.position = 'absolute';
        box.style.top = rect.top + 'px';
        box.style.left = rect.left + 'px';
        box.style.width = rect.width + 'px';
        box.style.height = rect.height + 'px';
        box.style.border = '2px solid rgba(255, 0, 85, 0.6)';
        box.style.boxSizing = 'border-box';
        
        container.appendChild(box);
        container.appendChild(label);
    });
    
    document.body.appendChild(container);
}
"""

SOM_CLEANUP_SCRIPT = """
() => {
    const container = document.getElementById('aboa-som-overlay-container');
    if (container) {
        container.remove();
    }
}
"""

class SoMAnnotator:
    @staticmethod
    async def annotate_and_screenshot(page: Page) -> str:
        """
        Draws Set-Of-Marks boxes over all elements tagged by the DOMExtracter,
        takes a screenshot, cleans up the drawing, and returns a Base64 JPEG string.
        """
        
        # 1. Inject Visual Overlays
        await page.evaluate(SOM_INJECTION_SCRIPT)
        
        # 2. Wait for visual paint
        await page.wait_for_timeout(200) 
        
        # 3. Capture Snapshot
        buffer = await page.screenshot(type="jpeg", quality=60)
        screenshot_b64 = base64.b64encode(buffer).decode("utf-8")
        
        # 4. Clean up overlays so future clicks don't hit the bounding boxes 
        # (Though pointer-events: none usually prevents this, keeping DOM clean is safer)
        await page.evaluate(SOM_CLEANUP_SCRIPT)
        
        return screenshot_b64
