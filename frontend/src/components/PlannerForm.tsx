// Purpose: Provide selectable inputs; no free-text prompt for faster happy path
import { useState } from "react";
import { planTrip } from "../api/client";
import type { PlanRequest, Itinerary } from "../types/app";

const CITIES = [
{ label: "Tokyo, Japan", value: { city: "Tokyo", country: "Japan" } },
{ label: "Paris, France", value: { city: "Paris", country: "France" } },
{ label: "Bangkok, Thailand", value: { city: "Bangkok", country: "Thailand" } }
];

const DURATIONS = [3, 5, 7, 10];
const BUDGETS = [500, 1000, 1500, 2000, 3000];
const PREFERENCES = ["food", "culture", "nature", "shopping", "nightlife", "family"];

export default function PlannerForm({ onPlan }: { onPlan: (it: Itinerary) => void }) {
// Local component state for form values
const [city, setCity] = useState(CITIES[0].value);
const [days, setDays] = useState(5);
const [budget, setBudget] = useState(1500);
const [prefs, setPrefs] = useState<string[]>(["food", "culture"]);
const [loading, setLoading] = useState(false);
const [err, setErr] = useState<string | null>(null);

const togglePref = (k: string) => setPrefs((p) => (p.includes(k) ? p.filter((x) => x !== k) : [...p, k]));

const submit = async () => {
    setLoading(true);
    setErr(null);
    try {
        const req: PlanRequest = {
        city: city.city,
        country: city.country,
        days,
        budget,
        currency: "USD",
        preferences: prefs
        };

        const it = await planTrip(req);
        onPlan(it);
    } catch (e: unknown) {
        let message = "Request failed";

        if (e instanceof Error) {
            message = e.message; // ✅ safe: Error always has .message
        }

  setErr(message);
    } finally {
        setLoading(false);
    }
};


    return (
        <div style={{ display: "grid", gap: 12 }}>
            <label>
                Destination
                <select value={city.city} onChange={(e) => setCity(CITIES.find((c) => c.value.city === e.target.value)!.value)}>
                    {CITIES.map((c) => (
                        <option key={c.label} value={c.value.city}>{c.label}</option>
                    ))}
                </select>
            </label>

            <label>
                Duration (days)
                <select value={days} onChange={(e) => setDays(parseInt(e.target.value))}>
                    {DURATIONS.map((d) => (<option key={d} value={d}>{d}</option>))}
                </select>
            </label>

            <label>
                Budget (USD)
                <select value={budget} onChange={(e) => setBudget(parseInt(e.target.value))}>
                    {BUDGETS.map((b) => (<option key={b} value={b}>{b}</option>))}
                </select>
            </label>

            <div>
                Preferences
                <div style={{ display: "flex", gap: 8, flexWrap: "wrap", marginTop: 6 }}>
                    {PREFERENCES.map((p) => (
                        <button
                            type="button"
                            key={p}
                            onClick={() => togglePref(p)}
                            style={{ padding: "6px 10px", borderRadius: 8, border: prefs.includes(p) ? "2px solid #333" : "1px solid #ccc", background: prefs.includes(p) ? "#eee" : "white", cursor: "pointer" }}
                        >{p}</button>
                    ))}
                </div>
            </div>

            <button onClick={submit} disabled={loading} style={{ padding: "8px 12px" }}>
                {loading ? "Planning..." : "Generate Plan"}
            </button>

            {err && <div style={{ color: "crimson" }}>{err}</div>}
        </div>
    );
}