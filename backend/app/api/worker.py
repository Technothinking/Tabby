import uuid
import asyncio
from app.api.ws import manager
from app.agent.planner.llm_client import LLMClient
from app.browser.driver import BrowserDriver
from app.agent.graph import build_graph

async def execute_run_task(run_id: uuid.UUID, goal: str):
    # Notify start
    print(f"Starting background task for run: {run_id}")
    await manager.broadcast_to_run(run_id, "run_status", {"status": "running"})
    
    try:
        driver = BrowserDriver()
        llm = LLMClient()
        context = await driver.new_context()
        page = await context.new_page()
        driver.current_page = page
        
        state = {
            "goal": goal,
            "constraints": {},
            "step_index": 0,
            "action_history": [],
            "status": "running"
        }
        
        graph = build_graph(driver, llm)
        config = {"configurable": {"thread_id": str(run_id)}, "recursion_limit": 25}
        
        # We use astream to intercept state updates and stream them to WS
        async for s in graph.astream(state, config=config):
            # Astream emits the state at the end of each node execution
            # s is a dict mapping node_name -> node_state_updates
            for node_name, state_update in s.items():
                print(f"Node {node_name} completed with state updates")    
                
                # We can broadcast a mock step so the UI moves
                step_data = {
                    "id": str(uuid.uuid4()),
                    "run_id": str(run_id),
                    "step_index": state_update.get("step_index", 0),
                    "node_name": node_name,
                    "status": "REQUIRE_HUMAN_APPROVAL" if state_update.get("status") == "REQUIRE_HUMAN_APPROVAL" else "completed",
                    "proposed_action": state_update.get("proposed_action", {}),
                    "observation_ref": state_update.get("observation", "")
                }
                await manager.broadcast_to_run(run_id, "step", step_data)
                
                # If required human approval, we can pause (graph naturally interrupts)
                
        # Finish
        await manager.broadcast_to_run(run_id, "run_status", {"status": "completed"})

    except Exception as e:
        print(f"Run crashed: {e}")
        await manager.broadcast_to_run(run_id, "run_status", {"status": "failed", "reason": str(e)})
    finally:
        await driver.close()
