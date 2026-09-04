"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Card } from "@/components/ui/card";
import { SectionTitle } from "@/components/ui/section-title";
import { apiGet, apiPost } from "@/services/api";

export default function RecoveryPage() {
  const queryClient = useQueryClient();
  const status = useQuery({ queryKey: ["recovery"], queryFn: () => apiGet<{ score: number }>("/recovery/status") });

  const addJournal = useMutation({
    mutationFn: () =>
      apiPost("/recovery/journal", {
        day: new Date().toISOString().slice(0, 10),
        hours_sleep: 7.5,
        quality_10: 7,
        fatigue_10: 4,
        soreness_10: 5,
        stress_10: 3,
        motivation_10: 8,
      }),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["recovery"] }),
  });

  const addSteps = useMutation({
    mutationFn: () => apiPost("/recovery/steps", { day: new Date().toISOString().slice(0, 10), steps: 8642 }),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["steps"] }),
  });

  return (
    <div className="space-y-5">
      <SectionTitle title="Recuperation" subtitle="Sommeil, fatigue, douleurs et activite" />

      <Card className="space-y-3">
        <p className="text-sm text-zinc-300">Score recup actuel: {status.data?.score ?? 0} / 100</p>
        <div className="flex gap-2">
          <button className="rounded-xl bg-cyan-500 px-4 py-2 text-sm font-semibold text-slate-950" onClick={() => addJournal.mutate()}>
            Ajouter journal
          </button>
          <button className="rounded-xl bg-emerald-400 px-4 py-2 text-sm font-semibold text-slate-950" onClick={() => addSteps.mutate()}>
            Ajouter pas du jour
          </button>
        </div>
      </Card>

      <Card>
        <h3 className="text-base font-semibold">Pain map</h3>
        <p className="mt-2 text-sm text-zinc-300">
          Selectionne epaules, pectoraux, dorsaux, dos, lombaires, biceps, triceps, quadriceps, ischios, fessiers, adducteurs, mollets,
          puis renseigne cote, intensite et type. L&apos;application ne pose pas de diagnostic medical.
        </p>
      </Card>
    </div>
  );
}
