import { create } from 'zustand';
import { type Run } from '../api/client';

interface RunStore {
    activeRun: Run | null;
    socket: WebSocket | null;
    setActiveRun: (run: Run) => void;
    connectToRun: (runId: string) => void;
    disconnect: () => void;
    sendApproval: (approved: boolean) => void;
}

export const useRunStore = create<RunStore>((set, get) => ({
    activeRun: null,
    socket: null,
    setActiveRun: (run) => set({ activeRun: run }),
    connectToRun: (runId) => {
        // Disconnect existing
        const existingSocket = get().socket;
        if (existingSocket) existingSocket.close();

        // Must use ws protocol and the proxy doesn't always automatically catch wss in Vite if not careful, 
        // We'll construct relative WS string
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        // In local development, the vite server runs on 5173 and proxies /ws. 
        const wsUrl = `${protocol}//${window.location.host}/ws/runs/${runId}`;

        console.log("Connecting to Run WebSocket:", wsUrl);
        const ws = new WebSocket(wsUrl);

        ws.onmessage = (event) => {
            const data = JSON.parse(event.data);
            console.log("WS Data", data);

            set((state) => {
                if (!state.activeRun) return state;
                const newRun = { ...state.activeRun };

                if (data.event === 'step') {
                    if (!newRun.steps) newRun.steps = [];
                    // Merge or append step
                    const existingIdx = newRun.steps.findIndex(s => s.id === data.data.id);
                    if (existingIdx >= 0) {
                        newRun.steps[existingIdx] = { ...newRun.steps[existingIdx], ...data.data };
                    } else {
                        newRun.steps.push(data.data);
                    }
                } else if (data.event === 'run_status') {
                    newRun.status = data.data.status;
                }

                return { activeRun: newRun };
            });
        };

        set({ socket: ws });
    },
    disconnect: () => {
        const { socket } = get();
        if (socket) socket.close();
        set({ activeRun: null, socket: null });
    },
    sendApproval: (approved: boolean) => {
        const { socket } = get();
        if (socket && socket.readyState === WebSocket.OPEN) {
            socket.send(JSON.stringify({ action: approved ? "approve" : "deny" }));
        }
    }
}));
