// Purpose: Render Google Map and markers from Itinerary JSON
import { useEffect, useRef } from "react";
import type { Itinerary } from "../types/app";

declare global { interface Window { google: any } }

function loadGoogleScript(apiKey: string) {
    // Inject Google Maps JS SDK once
    if (!apiKey) return;
    const id = "google-maps-js";

    if (document.getElementById(id)) return;
    const s = document.createElement("script");

    s.id = id;
    s.src = `https://maps.googleapis.com/maps/api/js?key=${apiKey}`;
    s.async = true;
    document.head.appendChild(s);
}

export default function MapView({ itinerary }: { itinerary: Itinerary | null }) {
    const divRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        loadGoogleScript(import.meta.env.VITE_GOOGLE_MAPS_API_KEY as string);
    }, []);

    useEffect(() => {
        // Guard: wait until map SDK and DOM container are ready
        if (!itinerary || !window.google || !divRef.current) return;

        // Choose a sensible center (first POI or fallback to Tokyo)
        const first = itinerary.days[0]?.items[0]?.poi;
        const center = first?.lat && first?.lng ? { lat: first.lat, lng: first.lng } : { lat: 35.6762, lng: 139.6503 };

        const map = new window.google.maps.Map(divRef.current, { center, zoom: 12 });

        // Add one marker per POI
        itinerary.days.forEach((d) => d.items.forEach((it) => {
            if (it.poi.lat && it.poi.lng) {
                new window.google.maps.Marker({ position: { lat: it.poi.lat, lng: it.poi.lng }, map, title: it.poi.name });
            }
        }));
    }, [itinerary]);


    return <div ref={divRef} style={{ width: "100%", height: 420, background: "#f3f3f3" }} />;
}