import re
from app.browser.actions import ProposedAction, ActionType

class IrreversibleClassifier:
    # Key phrases that denote destructive or high-risk financial actions
    KEYWORDS = [
        r"\bpay\b", r"\bpurchase\b", r"\bplace order\b", r"\bconfirm order\b",
        r"\bsubmit payment\b", r"\bdelete\b", r"\bremove account\b",
        r"\bcancel subscription\b", r"\bsend money\b", r"\btransfer funds\b"
    ]
    
    @classmethod
    def is_irreversible(cls, action: ProposedAction, dom_element_text: str = "") -> bool:
        """
        Rule-based classifier to catch obvious irreversible/financial intents.
        Checks the action's rationale, value, and the inferred target element text.
        """
        # Only clicks and types are typically irreversible triggers, but we'll scan anyway
        if action.type not in [ActionType.CLICK, ActionType.TYPE]:
            return False
            
        combined_text = " ".join(filter(None, [action.rationale, action.value, action.expected_effect, dom_element_text])).lower()
        
        for pattern in cls.KEYWORDS:
            if re.search(pattern, combined_text):
                return True
                
        return False
