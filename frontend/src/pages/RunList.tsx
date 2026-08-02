import { useEffect, useState } from "react";
import { useLocation } from "wouter";
import { getRuns, createRun, type Run } from "../api/client";
import { PlusCircle, Activity, CheckCircle, XCircle, Clock } from "lucide-react";

export function RunList() {
    const [runs, setRuns] = useState<Run[]>([]);
    const [goal, setGoal] = useState("");
    const [loading, setLoading] = useState(false);
    const [, setLocation] = useLocation();

    useEffect(() => {
        getRuns().then(setRuns).catch(console.error);
    }, []);

    const handleCreate = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!goal) return;
        setLoading(true);
        try {
            const run = await createRun(goal);
            setLocation(`/runs/${run.id}`);
        } catch (e) {
            alert("Failed to create run.");
        } finally {
            setLoading(false);
        }
    };

    const getStatusIcon = (status: string) => {
        switch (status) {
            case "running": return <Activity className="text-blue-400" />;
            case "completed": return <CheckCircle className="text-green-400" />;
            case "aborted":
            case "failed": return <XCircle className="text-red-400" />;
            default: return <Clock className="text-gray-400" />;
        }
    };

    return (
        <div className="container">
            <h1 className="header">Agent Orchestrator</h1>

            <form onSubmit={handleCreate} className="create-form">
                <input
                    type="text"
                    value={goal}
                    onChange={(e) => setGoal(e.target.value)}
                    placeholder="Enter a task goal for the agent..."
                    disabled={loading}
                    className="goal-input"
                />
                <button type="submit" disabled={loading || !goal} className="create-btn">
                    <PlusCircle size={18} /> Run
                </button>
            </form>

            <div className="run-grid">
                {runs.map(run => (
                    <div key={run.id} className="run-card" onClick={() => setLocation(`/runs/${run.id}`)}>
                        <div className="run-card-header">
                            <span className="run-id">{run.id.split('-')[0]}</span>
                            <span className="run-status">{getStatusIcon(run.status)} {run.status}</span>
                        </div>
                        <p className="run-goal">{run.goal}</p>
                    </div>
                ))}
            </div>
        </div>
    );
}
