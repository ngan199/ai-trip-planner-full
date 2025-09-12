// Purpose: Minimal form to add local knowledge documents for RAG (admin/dev use)
import { useState } from "react";
import { addRagDoc } from "../api/client";
import React from "react";

export default function RagAdmin() {
  const [title, setTitle] = useState<string>("");
  const [city, setCity] = useState<string>("");
  const [content, setContent] = useState<string>("");
  const [msg, setMsg] = useState<string>("");

  async function submit() {
    setMsg("");
    try {
      await addRagDoc(title, city, content);
      setMsg("Document added.");
      setTitle(""); setCity(""); setContent("");
    } catch (e) {
      setMsg(String(e));
    }
  }

  return (
    <div style={{ border: "1px dashed #aaa", padding: 12, borderRadius: 8 }}>
      <h3>RAG — Add Local Knowledge</h3>
      <label>Title <input value={title} onChange={(e) => setTitle(e.target.value)} /></label>
      <label>City <input value={city} onChange={(e) => setCity(e.target.value)} /></label>
      <label>Content <textarea value={content} onChange={(e) => setContent(e.target.value)} rows={5} /></label>
      <button onClick={submit}>Add Doc</button>
      {msg && <div style={{ marginTop: 6 }}>{msg}</div>}
    </div>
  );
}
