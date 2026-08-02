import { useEffect, useState } from "react";
import { useParams, Link } from "wouter";
import { getRun } from "../api/client";
import { useRunStore } from "../store/useRunStore";
import { ChevronLeft, Terminal, AlertTriangle } from "lucide-react";
import { ApprovalModal } from "../components/ApprovalModal";

export function RunViewer() {
    const { id } = useParams();
    const { activeRun, setActiveRun, connectToRun, disconnect, currentScreenshot } = useRunStore();
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        if (!id) return;
        setLoading(true);
        // Initial fetch
        getRun(id).then(run => {
            setActiveRun(run);
            setLoading(false);
            // Connect socket for live streaming
            connectToRun(run.id);
        }).catch(err => {
            console.error(err);
            setLoading(false);
        });

        return () => disconnect();
    }, [id, setActiveRun, connectToRun, disconnect]);

    if (loading) return <div className="loader">Loading Phase...</div>;
    if (!activeRun) return <div>Run not found.</div>;

    const requiresApproval = activeRun.steps?.find(s => s.status === 'REQUIRE_HUMAN_APPROVAL');

    return (
        <div className="viewer-container">
            {requiresApproval && <ApprovalModal step={requiresApproval} />}

            <header className="viewer-header">
                <Link href="/" className="back-link"><ChevronLeft /> Back</Link>
                <div className="header-details">
                    <span className="run-goal">{activeRun.goal}</span>
                    <span className={`status-badge ${activeRun.status}`}>{activeRun.status}</span>
                </div>
            </header>

            <div className="viewer-layout">
                {/* STEP TRACE SIDEBAR */}
                <aside className="steps-sidebar">
                    <h2><Terminal size={18} /> Execution Trace</h2>
                    <ul className="step-list">
                        {activeRun.steps?.map(step => (
                            <li key={step.id} className={`step-item ${step.status}`}>
                                <div className="step-header">
                                    <span className="step-num">#{step.step_index}</span>
                                    <span className="step-node">{step.node_name}</span>
                                </div>
                                {step.status === 'REQUIRE_HUMAN_APPROVAL' && (
                                    <div className="step-warning">
                                        <AlertTriangle size={14} /> Guardrail Pause
                                    </div>
                                )}
                                {step.proposed_action && (
                                    <div className="step-action">
                                        {step.proposed_action.type} {step.proposed_action.target_id ? `-> ${step.proposed_action.target_id}` : ''}
                                    </div>
                                )}
                            </li>
                        ))}
                        {(!activeRun.steps || activeRun.steps.length === 0) && (
                            <div className="empty-steps">Initializing planner...</div>
                        )}
                    </ul>
                </aside>

                {/* VISUAL PANEL (Screenshot / Output) */}
                <main className="viewer-main">
                    <div className="screen-frame">
                        {currentScreenshot ? (
                            <img src={`data:image/jpeg;base64,${currentScreenshot}`} alt="Live Agent View" className="live-screenshot" />
                        ) : (
                            <div className="screen-placeholder">
                                <div className="scan-line"></div>
                                {activeRun.status === 'running' ? 'Observing Environment...' : 'Task Terminated'}
                            </div>
                        )}
                    </div>
                </main>
            </div>
        </div>
    );
}
