from playwright.async_api import Page
from .grounded_observation import GroundedObservation

# This script finds interactive elements, tags them with data-aboa-id, and emits a structured list.
# We focus on a, button, input, select, textarea, and anything with a clickable role or tabindex.
INJECTION_SCRIPT = """
() => {
    let idCounter = 1;
    const items = [];
    
    // Select elements that are typically interactive
    const selector = 'a, button, input, select, textarea, [role="button"], [role="link"], [role="checkbox"], [role="menuitem"], [role="tab"], [tabindex]';
    const elements = document.querySelectorAll(selector);
    
    elements.forEach(el => {
        // Skip hidden elements
        const style = window.getComputedStyle(el);
        if (style.display === 'none' || style.visibility === 'hidden' || el.offsetWidth === 0 || el.offsetHeight === 0) {
            return;
        }

        // Assign stable ID
        const aboaId = 'el_' + idCounter++;
        el.setAttribute('data-aboa-id', aboaId);
        
        const tagName = el.tagName.toLowerCase();
        let name = el.getAttribute('aria-label') || el.innerText || el.value || el.placeholder || '';
        name = name.trim().replace(/\\n/g, ' ').substring(0, 100);
        
        let type = tagName;
        if (tagName === 'input') {
            type = el.getAttribute('type') || 'text';
        }
        
        let props = [];
        if (el.disabled) props.push('disabled');
        else props.push('enabled');
        
        if (el.value !== undefined && el.value !== null && tagName !== 'button' && type !== 'submit') {
            props.push(`value="${el.value}"`);
        }
        
        const propStr = props.length ? ` (${props.join(', ')})` : '';
        const nameStr = name ? ` "${name}"` : '';
        
        items.push(`[${aboaId}] ${type}${nameStr}${propStr}`);
    });
    
    return items.join('\\n');
}
"""

class DOMExtractor:
    @staticmethod
    async def extract(page: Page) -> GroundedObservation:
        # Run the injection script on the page
        dom_text = await page.evaluate(INJECTION_SCRIPT)
        
        # In a real implementation we would recursively extract from iframes,
        # but for this iteration we cover the root frame.
        return GroundedObservation(dom_text=dom_text)
