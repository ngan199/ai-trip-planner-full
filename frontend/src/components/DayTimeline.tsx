// Purpose: Readable day-by-day itinerary with optional source link (Google Maps URL)
import type { Itinerary } from "../types/app";               // Import Itinerary type for strong typing

export default function DayTimeline({ itinerary }: { itinerary: Itinerary | null }) {
  if (!itinerary) return <div>No itinerary yet</div>;        // Early return if nothing to show
  return (
    <div>
      {itinerary.days.map((d, idx) => (                      // Iterate each day in itinerary
        <div key={idx} style={{ marginBottom: 16 }}>
          <h3>Day {idx + 1} — {d.date}</h3>                  {/* Heading with index and date */}
          <ul>
            {d.items.map((it, i) => (                        // Iterate each item in the day
              <li key={i}>
                <strong>{it.time}</strong> — {it.poi.name}   {/* Time and POI name */}
                {typeof it.poi.rating === "number" && (      // Show rating if available
                  <> (⭐ {it.poi.rating.toFixed(1)})</>
                )}
                {it.transport && (                           // Show transit info if available
                  <> · {it.transport.mode} ~ {it.transport.duration_min}′</>
                )}
                {it.source?.type === "maps" && it.source?.place_id && (  // If source is Google Maps
                  <>
                    {" "}· <a
                      href={`https://www.google.com/maps/place/?q=place_id:${it.source.place_id}`}
                      target="_blank"
                      rel="noreferrer"
                    >Map</a>
                  </>
                )}
              </li>
            ))}
          </ul>
        </div>
      ))}
    </div>
  );
}
