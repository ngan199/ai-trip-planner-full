// Purpose: Button that generates a hotel booking link and opens in new tab
import { useState } from "react";
import { hotelIntent } from "../api/client";
import React from "react";

export default function BookingButton({ city, checkin, nights }: { city: string; checkin: string; nights: number }) {
  const [loading, setLoading] = useState<boolean>(false);
  const [src, setSrc] = useState<string>("");

  async function go() {
    setLoading(true);
    try {
      const data = await hotelIntent(city, checkin, nights);
      setSrc(`(${data.source})`);
      window.open(data.url, "_blank");
    } catch (e) {
      alert(String(e));
    } finally {
      setLoading(false);
    }
  }

  return (
    <button onClick={go} disabled={loading} style={{ padding: "6px 10px" }}>
      {loading ? "Preparing…" : "Book Hotels"} {src}
    </button>
  );
}
