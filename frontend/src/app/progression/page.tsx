"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Card } from "@/components/ui/card";
import { SectionTitle } from "@/components/ui/section-title";
import { apiGet, apiPost } from "@/services/api";
import { Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

type MeasurementRow = {
  id: string;
  day: string;
  weight_kg: number;
  waist_cm: number;
};

export default function ProgressionPage() {
  const queryClient = useQueryClient();
  const measurements = useQuery({
    queryKey: ["measurements"],
    queryFn: () => apiGet<MeasurementRow[]>("/progression/measurements"),
  });

  const addMeasurement = useMutation({
    mutationFn: () =>
      apiPost("/progression/measurements", {
        day: new Date().toISOString().slice(0, 10),
        weight_kg: 96.8,
        waist_cm: 90.9,
        chest_cm: 108.5,
        shoulders_cm: 126,
        arms_cm: 39,
        thighs_cm: 63,
        hips_cm: 101,
        body_fat_pct: 22,
        muscle_mass_kg: 40.5,
        body_water_pct: 52,
      }),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["measurements"] }),
  });

  return (
    <div className="space-y-5">
      <SectionTitle title="Progression corporelle" subtitle="Poids, mensurations et tendances" />

      <Card>
        <button className="rounded-xl bg-cyan-500 px-4 py-2 text-sm font-semibold text-slate-950" onClick={() => addMeasurement.mutate()}>
          Ajouter mesure du jour
        </button>
      </Card>

      <Card>
        <h3 className="text-base font-semibold">Poids et taille</h3>
        <div className="mt-3 h-60">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={measurements.data || []}>
              <XAxis dataKey="day" hide />
              <YAxis yAxisId="left" hide />
              <YAxis yAxisId="right" orientation="right" hide />
              <Tooltip />
              <Line yAxisId="left" type="monotone" dataKey="weight_kg" stroke="#22d3ee" strokeWidth={2} dot={false} />
              <Line yAxisId="right" type="monotone" dataKey="waist_cm" stroke="#f97316" strokeWidth={2} dot={false} />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </Card>

      <Card>
        <h3 className="text-base font-semibold">Historique</h3>
        <div className="mt-3 space-y-2 text-sm text-zinc-300">
          {(measurements.data || []).slice(-12).map((m) => (
            <div key={m.id} className="flex justify-between rounded-lg border border-white/10 px-3 py-2">
              <span>{m.day}</span>
              <span>{m.weight_kg} kg | taille {m.waist_cm} cm</span>
            </div>
          ))}
        </div>
      </Card>
    </div>
  );
}
