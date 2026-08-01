import pytest
import os
import asyncio
from app.browser.driver import BrowserDriver
from app.agent.planner.llm_client import FakeLLMClient
from app.agent.graph import build_graph
from app.browser.actions import ProposedAction, ActionType

@pytest.mark.asyncio
async def test_langgraph_loop():
    # Use a fake LLM that executes a hardcoded script to fill a form and click finish
    fake_actions = [
        ProposedAction(
            type=ActionType.TYPE,
            target_id="el_2", # The input Destination City in dom_test.html
            value="London",
            expected_effect="Text input should contain London",
            rationale="Typing destination",
            confidence="high"
        ),
        ProposedAction(
            type=ActionType.CLICK,
            target_id="el_4", # Search flights button
            expected_effect="Form submitted",
            rationale="Submitting the form",
            confidence="high"
        ),
        ProposedAction(
            type=ActionType.FINISH,
            expected_effect="Stop loop",
            rationale="Finished",
            confidence="high"
        )
    ]
    
    llm_client = FakeLLMClient(predefined_actions=fake_actions)
    driver = BrowserDriver()
    
    # Pre-setup browser to a local HTML file content
    context = await driver.new_context()
    page = await context.new_page()
    driver.current_page = page
    
    html_content = ""
    with open("tests/fixtures/pages/dom_test.html", "r") as f:
        html_content = f.read()
    await page.set_content(html_content, wait_until="networkidle")
    
    # Initialize state
    state = {
        "goal": "Fill destination and click search",
        "constraints": {},
        "step_index": 0,
        "action_history": [],
        "status": "running"
    }
    
    graph = build_graph(driver, llm_client)
    config = {"configurable": {"thread_id": "test_basic_loop"}, "recursion_limit": 25}
    
    # Invoke the graph natively
    final_state = await graph.ainvoke(state, config=config)
    
    await driver.close()
    
    # Assertions
    assert final_state["status"] == "completed"
    assert final_state["proposed_action"].type.value == "finish"
    assert len(final_state["action_history"]) == 2 # Only Type and Click are executed (FINISH ends graph before ACT)
