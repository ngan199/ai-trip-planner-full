// Defines TypeScript types that mirror backend Pydantic models.
// This enforces a stable contract between FE and BE at compile time.

export type PlanRequest = {
    city: string; // Target city for the trip
    country?: string; // Optional country to disambiguate the query
    start_date?: string; // Optional start date (YYYY-MM-DD) or label
    days: number; // Trip length in days
    budget: number; // Target budget for the whole trip
    travelers?: number; // Number of travelers (default 1)
    currency?: string; // Currency code (e.g., USD)
    preferences?: string[]; // High-level interests (e.g., food, culture)
};

export type Source = {
    type: "maps" | "rag" | "user" | "provider"; // Where the data came from
    url?: string; // Optional link (e.g., Google Maps URL)
    place_id?: string; // Google Place ID when type === "maps"
};

export type Cost = { amount: number; currency: string };

export type Transport = {
    mode: "walk" | "metro" | "bus" | "car" | "train" | "flight"; // Transport mode
    duration_min: number; // Travel time in minutes
    distance_km?: number; // Optional distance in kilometers
};

export type POI = {
    name: string; // Place display name
    address?: string; // Formatted address
    place_id?: string; // Unique Google identifier
    rating?: number; // Average rating
    lat?: number; // Latitude
    lng?: number; // Longitude
};

export type DayItem = {
    time: string; // Suggested start time for this item
    poi: POI; // Place details
    transport?: Transport; // How to get here from the previous item
    cost?: Cost; // Optional cost for this item
    source?: Source; // Provenance of the data
    notes?: string; // Optional notes to display in UI
};

export type DayPlan = { date: string; items: DayItem[] };

export type Totals = {
    lodging: number; // Aggregate cost buckets (mocked in Sprint 1)
    food: number;
    transport: number;
    tickets: number;
    misc: number;
    currency: string; // Currency for totals
};

export type TripInfo = { city: string; days: number; currency: string; budget: number };

export type Itinerary = {
    trip: TripInfo;
    days: DayPlan[];
    totals: Totals;
    notes: string[]; // Notes and disclaimers
    uncertainties: string[]; // Items that require user attention/confirmation
};