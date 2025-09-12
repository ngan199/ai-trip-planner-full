// Purpose: Compose the page layout and hold the Itinerary state
import { useState } from "react";
import PlannerForm from "./components/PlannerForm";
import MapView from "./components/MapView";
import DayTimeline from "./components/DayTimeline";
import BudgetBreakdown from "./components/BudgetBreakdown";
import Notes from "./components/Notes";
import type { Itinerary } from "./types/app";


export default function App() {
  const [itinerary, setItinerary] = useState<Itinerary | null>(null);


  return (
    <div style={{ display: "grid", gridTemplateColumns: "380px 1fr", gap: 16, padding: 16 }}>
      <div>
        <h2 style={{ marginTop: 0 }}>AI Travel Planner</h2>
        <PlannerForm onPlan={setItinerary} />
        <div style={{ marginTop: 16 }}>
          <BudgetBreakdown itinerary={itinerary} />
        </div>
      </div>
      <div>
        <MapView itinerary={itinerary} />
        <div style={{ marginTop: 16 }}>
          <DayTimeline itinerary={itinerary} />
          <Notes notes={itinerary?.notes} uncertainties={itinerary?.uncertainties} />  {/* new */}
        </div>
      </div>
    </div>
  );
}