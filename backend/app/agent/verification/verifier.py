from app.agent.state import VerificationResult, AgentState

class Verifier:
    @staticmethod
    async def verify(state: AgentState) -> VerificationResult:
        # For this iteration, we do a simple heuristic check based on the action result.
        # If the action result succeeded and we navigated or clicked, we'll assume success for now.
        # In a strict implementation, we would diff the DOM pre/post against `expected_effect`.
        action = state.get("proposed_action")
        last_action_exec = state["action_history"][-1] if state.get("action_history") else None
        
        if not action or not last_action_exec:
            return {"success": False, "reason": "No action to verify"}
            
        if last_action_exec.get("result_status"):
            return {"success": True, "reason": f"Expected effect '{action.expected_effect}' assumed achieved on successful execution"}
        else:
            return {"success": False, "reason": last_action_exec.get("result_message", "Action failed to execute")}
