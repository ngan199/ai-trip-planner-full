// Purpose: Simple, readable day-by-day itinerary renderer
import type { Itinerary } from "../types/app";

export default function DayTimeline({ itinerary }: { itinerary: Itinerary | null }) {
    if (!itinerary) return <div>No itinerary yet</div>;
    
    return (
        <div>
            {itinerary.days.map((d, idx) => (
                <div key={idx} style={{ marginBottom: 16 }}>
                    <h3>Day {idx + 1} — {d.date}</h3>
                    <ul>
                        {d.items.map((it, i) => (
                        <li key={i}>
                            <strong>{it.time}</strong> — {it.poi.name} (⭐ {it.poi.rating ?? "-"})
                            {it.transport && <> · {it.transport.mode} ~ {it.transport.duration_min}′</>}
                        </li>
                        ))}
                    </ul>
                </div>
            ))}
        </div>
    );
}