import asyncio
from app.browser.driver import BrowserDriver
from app.agent.state import AgentState
from app.agent.graph import perceive

async def test_som():
    driver = BrowserDriver()
    try:
        context = await driver.new_context()
        page = await context.new_page()
        driver.current_page = page
        
        # We need to construct a url for the backend container to reach the file
        # Using a direct file:// URL path for the fixture
        await page.goto("http://backend:8080/canvas_test.html")
        
        state = {
            "goal": "Click the real button labelled Purchase Hidden Item",
            "step_index": 1
        }
        
        result = await perceive(state, driver)
        
        print("\\n--- PERCEIVE COMPLETED ---")
        print("Heuristic triggered SOM?", result["observation"].needs_som_fallback)
        print("Resulting Modded DOM Text:\\n")
        print(result["observation"].dom_text)
        
    finally:
        await driver.close()

if __name__ == "__main__":
    asyncio.run(test_som())
