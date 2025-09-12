// Purpose: Simple login/register panel; stores token in localStorage on success
import { useState } from "react";
import { login, register } from "../api/client";
import React from "react";

export default function Auth() {
  const [email, setEmail] = useState<string>("");
  const [pw, setPw] = useState<string>("");
  const [mode, setMode] = useState<"login" | "register">("login");
  const [msg, setMsg] = useState<string>("");

  async function submit() {
    setMsg("");
    try {
      if (mode === "login") await login(email, pw);
      else await register(email, pw);
      setMsg("Success!");
    } catch (e) {
      setMsg(String(e));
    }
  }

  return (
    <div style={{ border: "1px solid #ddd", padding: 12, borderRadius: 8 }}>
      <h3>Account</h3>
      <label>Email <input value={email} onChange={(e) => setEmail(e.target.value)} /></label>
      <label>Password <input type="password" value={pw} onChange={(e) => setPw(e.target.value)} /></label>
      <div style={{ display: "flex", gap: 8, marginTop: 6 }}>
        <button onClick={() => setMode("login")} disabled={mode === "login"}>Login</button>
        <button onClick={() => setMode("register")} disabled={mode === "register"}>Register</button>
      </div>
      <button onClick={submit} style={{ marginTop: 8 }}>Submit</button>
      {msg && <div style={{ marginTop: 6 }}>{msg}</div>}
    </div>
  );
}
