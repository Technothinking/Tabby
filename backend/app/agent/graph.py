from langgraph.graph import StateGraph, END
from app.agent.state import AgentState, ExecutedAction
from app.agent.planner.llm_client import LLMClient
from app.agent.planner.prompts import SYSTEM_PROMPT, USER_PROMPT
from app.agent.grounding.dom_extractor import DOMExtractor
from app.agent.verification.verifier import Verifier
from app.browser.actions import ActionDispatcher, ActionType
from app.browser.driver import BrowserDriver

async def perceive(state: AgentState, driver: BrowserDriver):
    page = driver.current_page
    if not page:
        return {"status": "failed", "finish_reason": "Browser page not found"}
        
    obs = await DOMExtractor.extract(page)
    return {"observation": obs, "step_index": state.get("step_index", 0) + 1}

async def plan(state: AgentState, llm_client: LLMClient):
    system_prompt = SYSTEM_PROMPT.format(memory_hints="\n".join(state.get("memory_hints", [])) or "None")
    
    action_history = "\n".join([f"{a['proposed_action'].type} - {a['result_status']}" for a in state.get("action_history", [])[-5:]])
    
    user_prompt = USER_PROMPT.format(
        goal=state.get("goal"),
        constraints_json=str(state.get("constraints", {})),
        step_index=state.get("step_index", 1),
        max_steps=40,
        action_history_tail=action_history or "None",
        observation_text=state.get("observation").dom_text if state.get("observation") else "None",
        last_verification=state.get("last_verification", "N/A - first step")
    )
    
    action = await llm_client.propose_action(system_prompt, user_prompt)
    if action.type == ActionType.FINISH:
        return {"proposed_action": action, "status": "completed", "finish_reason": action.rationale}
    return {"proposed_action": action, "status": "running"}

async def act(state: AgentState, driver: BrowserDriver):
    page = driver.current_page
    action = state.get("proposed_action")
    
    result = await ActionDispatcher.execute(page, action)
    
    executed: ExecutedAction = {
        "proposed_action": action,
        "result_status": result.success,
        "result_message": result.message
    }
    
    history = state.get("action_history", [])
    history.append(executed)
    return {"action_history": history}

async def verify(state: AgentState):
    ver = await Verifier.verify(state)
    return {"last_verification": ver}

def route_after_plan(state: AgentState):
    if state.get("status") == "completed":
        return END
    return "act"

def build_graph(driver: BrowserDriver, llm_client: LLMClient):
    graph = StateGraph(AgentState)
    
    # Standardize nodes using partial evaluation or by wrapping with the context.
    # In a real environment, we use contextvars or configuration passed into the invoke call.
    async def perceive_node(state: AgentState):
        return await perceive(state, driver)
        
    async def plan_node(state: AgentState):
        return await plan(state, llm_client)
        
    async def act_node(state: AgentState):
        return await act(state, driver)
        
    async def verify_node(state: AgentState):
        return await verify(state)
        
    graph.add_node("perceive", perceive_node)
    graph.add_node("plan", plan_node)
    graph.add_node("act", act_node)
    graph.add_node("verify", verify_node)
    
    graph.set_entry_point("perceive")
    
    graph.add_edge("perceive", "plan")
    
    graph.add_conditional_edges("plan", route_after_plan, {END: END, "act": "act"})
    
    graph.add_edge("act", "verify")
    graph.add_edge("verify", "perceive")
    
    return graph.compile()
