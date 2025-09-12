// Defines TypeScript types that mirror backend Pydantic models.
// This enforces a stable contract between FE and BE at compile time.

export type PlanRequest = {
  city: string;                 // Target city for the trip
  country?: string;             // Optional country to disambiguate the query
  start_date?: string;          // Optional start date (YYYY-MM-DD) or label
  days: number;                 // Trip length in days
  budget: number;               // Target budget for the whole trip
  travelers?: number;           // Number of travelers (default 1)
  currency?: string;            // Currency code (e.g., USD)
  preferences?: string[];       // High-level interests (e.g., food, culture)
};

export type Source = {
  type: "maps" | "rag" | "user" | "provider"; // Where the data came from
  url?: string;                                // Optional link (e.g., Google Maps URL)
  place_id?: string;                           // Google Place ID when type === "maps"
};

export type Cost = { amount: number; currency: string };

export type Transport = {
  mode: "walk" | "metro" | "bus" | "car" | "train" | "flight";
  duration_min: number;
  distance_km?: number;
};

export type POI = {
  name: string;
  address?: string;
  place_id?: string;
  rating?: number;
  lat?: number;
  lng?: number;
};

export type DayItem = {
  time: string;
  poi: POI;
  transport?: Transport;
  cost?: Cost;
  source?: Source;
  notes?: string;
};

export type DayPlan = { date: string; items: DayItem[] };

export type Totals = {
  lodging: number;
  food: number;
  transport: number;
  tickets: number;
  misc: number;
  currency: string;
};

export type TripInfo = { city: string; days: number; currency: string; budget: number };

// ---- Budget explain typing (replaces `any`) ----
export type BudgetCategory = "lodging" | "food" | "transport" | "tickets" | "misc";

export type BudgetExplainItem = {
  source: string;          // e.g., "Google Hotels", "User input", "Provider XYZ"
  currency: string;        // e.g., "USD"
  // Optional fields depending on category
  nightly?: number;        // typical for lodging
  nights?: number;         // typical for lodging
  per_day?: number;        // typical for food/transport
  note?: string;           // free-form explanation
};

// Optional object keyed by category; each entry is explained data
export type BudgetExplain = Partial<Record<BudgetCategory, BudgetExplainItem>>;

export type Itinerary = {
  trip: TripInfo;
  days: DayPlan[];
  totals: Totals;
  notes: string[];
  uncertainties: string[];
  /** Optional explain block attached by backend (Sprint 1: often only `lodging`) */
  budget_explain?: BudgetExplain;
};
