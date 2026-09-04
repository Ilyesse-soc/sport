"use client";

import { useState } from "react";
import { useMutation } from "@tanstack/react-query";
import { Card } from "@/components/ui/card";
import { SectionTitle } from "@/components/ui/section-title";
import { apiPost } from "@/services/api";

export default function CoachPage() {
  const [message, setMessage] = useState("Fais mon analyse du jour");
  const [history, setHistory] = useState<{ role: string; content: string }[]>([]);

  const chat = useMutation({
    mutationFn: () => apiPost<{ answer: string }>("/coach/chat", { message }),
    onSuccess: (data) => {
      setHistory((prev) => [...prev, { role: "user", content: message }, { role: "assistant", content: data.answer }]);
      setMessage("");
    },
  });

  return (
    <div className="space-y-5">
      <SectionTitle title="COACH IA" subtitle="Conseils data-driven, sans diagnostic medical" />
      <Card className="space-y-3">
        <textarea
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          className="min-h-24 w-full rounded-xl border border-white/10 bg-black/30 p-3 text-sm outline-none"
        />
        <button className="rounded-xl bg-cyan-500 px-4 py-2 text-sm font-semibold text-slate-950" onClick={() => chat.mutate()}>
          Envoyer
        </button>
      </Card>

      <div className="space-y-3">
        {history.map((m, index) => (
          <Card key={`${m.role}-${index}`} className={m.role === "assistant" ? "border-cyan-400/30" : ""}>
            <p className="text-xs uppercase text-zinc-500">{m.role === "assistant" ? "Coach" : "Vous"}</p>
            <p className="mt-1 text-sm text-zinc-100">{m.content}</p>
          </Card>
        ))}
      </div>
    </div>
  );
}
