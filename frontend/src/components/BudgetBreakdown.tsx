// Purpose: Show budget categories and total
import type { Itinerary } from "../types/app";

export default function BudgetBreakdown({ itinerary }: { itinerary: Itinerary | null }) {
    if (!itinerary) return null;
        const t = itinerary.totals;
        const total = t.lodging + t.food + t.transport + t.tickets + t.misc;

        return (
            <div style={{ border: "1px solid #ddd", padding: 12, borderRadius: 8 }}>
                <h3>Budget</h3>
                <div>Lodging: {t.lodging} {t.currency}</div>
                <div>Food: {t.food} {t.currency}</div>
                <div>Transport: {t.transport} {t.currency}</div>
                <div>Tickets: {t.tickets} {t.currency}</div>
                <div>Misc: {t.misc} {t.currency}</div>
                <hr />
                <strong>Total: {total} {t.currency}</strong>
            </div>
        );
}