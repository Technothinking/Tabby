export interface Step {
    id: string;
    run_id: string;
    step_index: number;
    node_name: string;
    observation_ref: any;
    proposed_action: any;
    guardrail_decision: string;
    action_result: any;
    verification_result: any;
    status: string;
    retry_count: number;
}

export interface Run {
    id: string;
    goal: string;
    status: string;
    steps?: Step[];
}

export const API_BASE = '/api/v1';

export async function createRun(goal: string, max_steps: number = 20): Promise<Run> {
    const res = await fetch(`${API_BASE}/runs`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ goal, max_steps })
    });
    if (!res.ok) throw new Error('Failed to create run');
    return res.json();
}

export async function getRuns(): Promise<Run[]> {
    const res = await fetch(`${API_BASE}/runs`);
    if (!res.ok) throw new Error('Failed to fetch runs');
    return res.json();
}

export async function getRun(id: string): Promise<Run> {
    const res = await fetch(`${API_BASE}/runs/${id}`);
    if (!res.ok) throw new Error('Failed to fetch run');
    return res.json();
}
