from typing import Literal
from app.browser.actions import ProposedAction
from app.agent.state import AgentState
from app.agent.guardrails.irreversible_classifier import IrreversibleClassifier

class GuardrailEngine:
    @staticmethod
    def evaluate(state: AgentState) -> Literal["ALLOW", "DENY", "REQUIRE_HUMAN_APPROVAL"]:
        action = state.get("proposed_action")
        if not action:
            return "ALLOW" # Nothing to block if no action
            
        # In the future, we could query the DOM extraction to get the exact button text for `dom_element_text`.
        # For now, we rely on the LLM's rationale and expected_effect.
        is_high_risk = IrreversibleClassifier.is_irreversible(action)
        
        if is_high_risk:
            # We fail close on high risk. Require human in the loop.
            return "REQUIRE_HUMAN_APPROVAL"
            
        # Other future checks (domain allow list, etc) would go here and might return "DENY"
        return "ALLOW"
