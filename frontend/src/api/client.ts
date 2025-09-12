// Purpose: HTTP client with optional bearer auth, typed endpoints
import type { PlanRequest, Itinerary } from "../types/app";

const BASE = (import.meta.env.VITE_BACKEND_URL as string) || "http://localhost:8000";

// Helper to read token from localStorage (if user logged in)
function authHeader(): Record<string, string> {
  const token = localStorage.getItem("token");
  return token ? { Authorization: `Bearer ${token}` } : {};
}

export async function planTrip(req: PlanRequest): Promise<Itinerary> {
  const res = await fetch(`${BASE}/api/agent/plan`, {
    method: "POST",
    headers: { "Content-Type": "application/json", ...authHeader() },
    body: JSON.stringify(req),
  });
  if (!res.ok) throw new Error(await res.text());
  return res.json() as Promise<Itinerary>;
}

// Auth
export async function register(email: string, password: string): Promise<void> {
  const res = await fetch(`${BASE}/auth/register`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password }),
  });
  if (!res.ok) throw new Error(await res.text());
  const data = (await res.json()) as { access_token: string };
  localStorage.setItem("token", data.access_token);
}

export async function login(email: string, password: string): Promise<void> {
  const res = await fetch(`${BASE}/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password }),
  });
  if (!res.ok) throw new Error(await res.text());
  const data = (await res.json()) as { access_token: string };
  localStorage.setItem("token", data.access_token);
}

// RAG admin
export async function addRagDoc(title: string, city: string, content: string): Promise<void> {
  const res = await fetch(`${BASE}/rag/docs`, {
    method: "POST",
    headers: { "Content-Type": "application/json", ...authHeader() },
    body: JSON.stringify({ title, city, content }),
  });
  if (!res.ok) throw new Error(await res.text());
}

// Trips
export async function saveTrip(title: string, itinerary: Itinerary): Promise<void> {
  const res = await fetch(`${BASE}/api/trips`, {
    method: "POST",
    headers: { "Content-Type": "application/json", ...authHeader() },
    body: JSON.stringify({ title, itinerary }),
  });
  if (!res.ok) throw new Error(await res.text());
}

export async function listTrips(): Promise<Array<{ id: number; title: string }>> {
  const res = await fetch(`${BASE}/api/trips`, { headers: { ...authHeader() } });
  if (!res.ok) throw new Error(await res.text());
  const data = (await res.json()) as Array<{ id: number; title: string; itinerary: Itinerary }>;
  return data.map((t) => ({ id: t.id, title: t.title }));
}

// Booking
export async function hotelIntent(city: string, checkin: string, nights: number): Promise<{ url: string; source: string }> {
  const res = await fetch(`${BASE}/api/booking/hotel-intent?city=${encodeURIComponent(city)}&checkin=${checkin}&nights=${nights}`);
  if (!res.ok) throw new Error(await res.text());
  return (await res.json()) as { url: string; source: string };
}
