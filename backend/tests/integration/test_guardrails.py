import pytest
import asyncio
from app.browser.driver import BrowserDriver
from app.agent.planner.llm_client import FakeLLMClient
from app.agent.graph import build_graph
from app.browser.actions import ProposedAction, ActionType

@pytest.mark.asyncio
async def test_guardrail_interrupt_on_irreversible():
    # Provide an action that looks like deleting an account
    fake_actions = [
        ProposedAction(
            type=ActionType.CLICK,
            target_id="el_3",
            value=None,
            expected_effect="Account deleted completely",
            rationale="User requested to delete their account.",
            confidence="high"
        )
    ]
    
    llm_client = FakeLLMClient(predefined_actions=fake_actions)
    driver = BrowserDriver()
    
    # Pre-setup browser to a local HTML file content
    context = await driver.new_context()
    page = await context.new_page()
    driver.current_page = page
    
    html_content = "<div><button data-aboa-id='el_3'>Delete Account</button></div>"
    await page.set_content(html_content, wait_until="networkidle")
    
    # Initialize state
    state = {
        "goal": "Delete my fake account",
        "constraints": {},
        "step_index": 0,
        "action_history": [],
        "status": "running"
    }
    
    graph = build_graph(driver, llm_client)
    config = {"configurable": {"thread_id": "test_1"}, "recursion_limit": 25}
    
    # Invoke the graph natively. Because it hits an `interrupt_before`, it will return the state at that point.
    final_state = await graph.ainvoke(state, config=config)
    
    await driver.close()
    
    # Assertions
    # It hasn't reached `act` yet, so action_history is empty
    assert len(final_state.get("action_history", [])) == 0
    # Guardrail caught it
    assert final_state["guardrail_decision"] == "REQUIRE_HUMAN_APPROVAL"
    # Action type remains the same
    assert final_state["proposed_action"].type.value == "click"

    # Ensure we actually paused in LangGraph instead of finishing execution
    # In LangGraph, if interrupted, the graph's get_state(config).next should indicate the pending node.
    checkpoint_state = graph.get_state(config)
    assert len(checkpoint_state.next) > 0
    assert checkpoint_state.next[0] == "human_approval"
