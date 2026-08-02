import { useRunStore } from "../store/useRunStore";
import { type Step } from "../api/client";

interface Props {
    step: Step;
}

export function ApprovalModal({ step }: Props) {
    const { sendApproval } = useRunStore();

    return (
        <div className="modal-overlay">
            <div className="modal-content glass">
                <h3 className="modal-title">Action Requires Approval</h3>
                <p className="modal-desc">
                    The agent planned an irreversible or high-risk action.
                </p>

                <div className="action-details">
                    <span className="action-type">{step.proposed_action?.type}</span>
                    <p className="action-rationale">{step.proposed_action?.rationale}</p>
                </div>

                <div className="modal-actions">
                    <button className="btn deny" onClick={() => sendApproval(false)}>Reject</button>
                    <button className="btn approve" onClick={() => sendApproval(true)}>Allow execution</button>
                </div>
            </div>
        </div>
    );
}
