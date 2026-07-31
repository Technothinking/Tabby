import pytest
import os
from app.browser.actions import ActionDispatcher, ProposedAction, ActionType

@pytest.mark.asyncio
async def test_action_navigate(page):
    fixture_path = f"file://{os.path.abspath('tests/fixtures/pages/test_page.html')}"
    action = ProposedAction(type=ActionType.NAVIGATE, target_id=None, value=fixture_path, expected_effect="Page loads")
    result = await ActionDispatcher.execute(page, action)
    assert result.success
    assert "Navigated to" in result.message

@pytest.mark.asyncio
async def test_action_type(page):
    fixture_path = f"file://{os.path.abspath('tests/fixtures/pages/test_page.html')}"
    await page.goto(fixture_path)
    
    action = ProposedAction(type=ActionType.TYPE, target_id="#username", value="testuser", expected_effect="Typed username")
    result = await ActionDispatcher.execute(page, action)
    
    assert result.success
    val = await page.locator("#username").input_value()
    assert val == "testuser"

@pytest.mark.asyncio
async def test_action_click(page):
    fixture_path = f"file://{os.path.abspath('tests/fixtures/pages/test_page.html')}"
    await page.goto(fixture_path)
    
    action = ProposedAction(type=ActionType.CLICK, target_id="#submit-btn", value=None, expected_effect="Clicked button")
    result = await ActionDispatcher.execute(page, action)
    
    assert result.success
    text = await page.locator("#result").inner_text()
    assert text == "Clicked!"

@pytest.mark.asyncio
async def test_action_screenshot(page):
    fixture_path = f"file://{os.path.abspath('tests/fixtures/pages/test_page.html')}"
    await page.goto(fixture_path)
    
    action = ProposedAction(type=ActionType.SCREENSHOT, target_id=None, value=None, expected_effect="Screenshot taken")
    result = await ActionDispatcher.execute(page, action)
    
    assert result.success
    assert result.data is not None
    assert isinstance(result.data, bytes)
