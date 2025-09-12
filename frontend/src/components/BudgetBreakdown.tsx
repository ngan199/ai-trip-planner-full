// Purpose: Show budget categories, total, and provider source if available
import type { Itinerary } from "../types/app";

export default function BudgetBreakdown({ itinerary }: { itinerary: Itinerary | null }) {
  if (!itinerary) return null;

  const t = itinerary.totals;
  const total = t.lodging + t.food + t.transport + t.tickets + t.misc;
  const explain = itinerary.budget_explain; // typed & optional

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

      {explain?.lodging && (
        <div style={{ marginTop: 8, fontSize: 12, opacity: 0.9 }}>
          Source: <em>{explain.lodging.source}</em> · Nightly ≈ {explain.lodging.nightly} {explain.lodging.currency} × {explain.lodging.nights} nights
        </div>
      )}
    </div>
  );
}
