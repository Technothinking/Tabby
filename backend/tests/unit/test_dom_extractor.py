import pytest
import os
from app.agent.grounding.dom_extractor import DOMExtractor
from app.browser.driver import BrowserDriver

@pytest.mark.asyncio
async def test_dom_extractor_identifies_interactives():
    driver = BrowserDriver()
    context = await driver.new_context()
    page = await context.new_page()
    
    # We must construct a valid URL for the backend container to read (or mount it, or serve it)
    # Since we are running test inside backend, we can use a file URL! 
    # Wait, the browser container executes the navigation, so file:// paths won't work in the browser container!
    # I should start a quick Python HTTP server to serve the fixture if needed, or inject HTML directly via set_content()
    
    html_content = ""
    with open("tests/fixtures/pages/dom_test.html", "r") as f:
        html_content = f.read()
    
    await page.set_content(html_content, wait_until="networkidle")
    
    observation = await DOMExtractor.extract(page)
    text = observation.dom_text
    
    await driver.close()
    
    # Assert elements are extracted and labeled correctly
    assert 'select "From City" (enabled, value="BOM")' in text
    assert 'text "BLR" (enabled, value="BLR")' in text
    assert 'checkbox "on" (enabled, value="on")' in text
    assert 'button "Search flights" (enabled)' in text
    assert 'a "Show filters" (enabled)' in text
    assert 'div "Custom clickable div" (enabled)' in text
    
    # Assert hidden elements are skipped
    assert "Invisible Admin Actions" not in text
    assert "Another Invisible" not in text
    
    # Assert aboa IDs are structured correctly
    assert "[el_1]" in text
    assert "[el_2]" in text
