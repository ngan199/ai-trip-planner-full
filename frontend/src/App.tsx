import { useState } from "react";
import PlannerForm from "./components/PlannerForm";
import MapView from "./components/MapView";
import DayTimeline from "./components/DayTimeline";
import BudgetBreakdown from "./components/BudgetBreakdown";
import Notes from "./components/Notes";
import Auth from "./components/Auth";
import RagAdmin from "./components/RagAdmin";
import BookingButton from "./components/BookingButton";
import type { Itinerary } from "./types/app";
import React from "react";

export default function App() {
  const [itinerary, setItinerary] = useState<Itinerary | null>(null);

  // Compute booking params from itinerary (first day as check-in)
  const city = itinerary?.trip.city ?? "Tokyo";
  const checkin = itinerary?.days[0]?.date ?? "2025-09-12";
  const nights = Math.max(1, (itinerary?.trip.days ?? 3) - 1);

  return (
    <div style={{ display: "grid", gridTemplateColumns: "380px 1fr", gap: 16, padding: 16 }}>
      <div>
        <h2 style={{ marginTop: 0 }}>AI Travel Planner</h2>
        <Auth />
        <div style={{ marginTop: 12 }}>
          <PlannerForm onPlan={setItinerary} />
        </div>
        <div style={{ marginTop: 12 }}>
          <RagAdmin />
        </div>
        <div style={{ marginTop: 16 }}>
          <BudgetBreakdown itinerary={itinerary} />
          {itinerary && (
            <div style={{ marginTop: 8 }}>
              <BookingButton city={city} checkin={checkin} nights={nights} />
            </div>
          )}
        </div>
      </div>
      <div>
        <MapView itinerary={itinerary} />
        <div style={{ marginTop: 16 }}>
          <DayTimeline itinerary={itinerary} />
          <Notes notes={itinerary?.notes} uncertainties={itinerary?.uncertainties} />
        </div>
      </div>
    </div>
  );
}
