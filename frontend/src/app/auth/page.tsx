"use client";

import { FormEvent, useState } from "react";
import { useRouter } from "next/navigation";
import { apiPost } from "@/services/api";

export default function AuthPage() {
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [firstName, setFirstName] = useState("");
  const [mode, setMode] = useState<"login" | "register">("login");
  const [error, setError] = useState("");

  async function onSubmit(event: FormEvent) {
    event.preventDefault();
    setError("");
    const path = mode === "login" ? "/auth/login" : "/auth/register";
    try {
      const data = await apiPost<{ access_token: string; user_id: string }>(
        path,
        mode === "login" ? { email, password } : { email, password, first_name: firstName },
      );
      window.localStorage.setItem("sport_token", data.access_token);
      window.localStorage.setItem("sport_user_id", data.user_id);
      router.push("/");
    } catch {
      setError("Echec authentification");
    }
  }

  return (
    <div className="mx-auto max-w-md">
      <form onSubmit={onSubmit} className="space-y-4 rounded-2xl border border-white/10 bg-black/30 p-5">
        <h1 className="text-2xl font-bold">Connexion</h1>
        <div className="flex gap-2 text-xs">
          <button type="button" className="rounded-lg border border-white/20 px-3 py-1" onClick={() => setMode("login")}>
            Login
          </button>
          <button type="button" className="rounded-lg border border-white/20 px-3 py-1" onClick={() => setMode("register")}>
            Register
          </button>
        </div>
        {mode === "register" ? (
          <input className="w-full rounded-xl border border-white/10 bg-black/20 px-3 py-2" value={firstName} onChange={(e) => setFirstName(e.target.value)} placeholder="Prenom" />
        ) : null}
        <input className="w-full rounded-xl border border-white/10 bg-black/20 px-3 py-2" value={email} onChange={(e) => setEmail(e.target.value)} placeholder="Email" />
        <input className="w-full rounded-xl border border-white/10 bg-black/20 px-3 py-2" type="password" value={password} onChange={(e) => setPassword(e.target.value)} placeholder="Mot de passe" />
        {error ? <p className="text-sm text-red-300">{error}</p> : null}
        <button className="w-full rounded-xl bg-cyan-400 px-3 py-2 font-semibold text-slate-900">Continuer</button>
      </form>
    </div>
  );
}
