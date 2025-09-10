// Minimal API client to call the backend planner endpoint.
// Keeps networking isolated from UI components.

import type { PlanRequest } from "../types/app";

const BASE = import.meta.env.VITE_BACKEND_URL || "http://localhost:8000"; // Configurable via env

export async function planTrip(req: PlanRequest) {
    // POST JSON body and expect JSON response
    const res = await fetch(`${BASE}/api/agent/plan`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(req)
    });

    if (!res.ok) {
        // Surface backend error payload to UI for better debugging
        const text = await res.text();
        throw new Error(`HTTP ${res.status}: ${text}`);
    }

    return res.json();
}