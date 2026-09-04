"use client";

import { useQuery } from "@tanstack/react-query";
import { Card } from "@/components/ui/card";
import { MetricProgress } from "@/components/ui/metric-progress";
import { SectionTitle } from "@/components/ui/section-title";
import { apiGet } from "@/services/api";
import { DailySummary, Goal } from "@/types/domain";
import { Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

type MeasurementPoint = { id: string; day: string; weight_kg: number };
type StepPoint = { day: string; steps: number };

export default function DashboardPage() {
  const today = new Date().toISOString().slice(0, 10);
  const goals = useQuery({ queryKey: ["goals"], queryFn: () => apiGet<Goal>("/profile/goals") });
  const summary = useQuery({
    queryKey: ["summary", today],
    queryFn: () => apiGet<DailySummary>(`/nutrition/daily-summary?day=${today}`),
  });
  const measurements = useQuery({
    queryKey: ["measurements"],
    queryFn: () => apiGet<MeasurementPoint[]>("/progression/measurements"),
  });
  const steps = useQuery({ queryKey: ["steps"], queryFn: () => apiGet<StepPoint[]>("/recovery/steps") });
  const recovery = useQuery({ queryKey: ["recovery"], queryFn: () => apiGet<{ score: number }>("/recovery/status") });

  const goal = goals.data;
  const day = summary.data;

  return (
    <div className="space-y-6">
      <SectionTitle title="Aujourd'hui" subtitle="Suivi nutrition, activite et recuperation" />

      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
        <Card className="space-y-3">
          <h3 className="text-sm uppercase text-zinc-400">Nutrition</h3>
          {goal && day ? (
            <div className="space-y-3">
              <MetricProgress label="Calories" value={day.calories} goal={goal.calories_kcal} unit=" kcal" />
              <MetricProgress label="Proteines" value={day.protein_g} goal={goal.protein_g} unit=" g" />
              <MetricProgress label="Glucides" value={day.carbs_g} goal={goal.carbs_g} unit=" g" />
              <MetricProgress label="Lipides" value={day.fats_g} goal={goal.fats_g} unit=" g" />
              <MetricProgress label="Fibres" value={day.fiber_g} goal={goal.fiber_g} unit=" g" />
            </div>
          ) : (
            <p className="text-sm text-zinc-400">Chargement...</p>
          )}
        </Card>

        <Card>
          <h3 className="text-sm uppercase text-zinc-400">Poids 30 jours</h3>
          <div className="mt-3 h-48">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={measurements.data || []}>
                <XAxis dataKey="day" hide />
                <YAxis domain={["dataMin - 1", "dataMax + 1"]} hide />
                <Tooltip />
                <Line type="monotone" dataKey="weight_kg" stroke="#22d3ee" strokeWidth={2} dot={false} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </Card>

        <Card className="space-y-3">
          <h3 className="text-sm uppercase text-zinc-400">Synthese IA</h3>
          <p className="text-sm text-zinc-200">
            {day && goal
              ? `Calories ${Math.round(day.calories)}/${goal.calories_kcal}, proteines ${Math.round(day.protein_g)}/${goal.protein_g}g. `
              : "En attente de donnees. "}
            {steps.data?.length ? "Pense a viser ton objectif de pas aujourd'hui. " : "Ajoute tes pas pour des recommandations plus precises. "}
            {recovery.data ? `Score recuperation: ${recovery.data.score}/100.` : "Ajoute ton journal de recuperation."}
          </p>
        </Card>
      </div>

      <div className="grid gap-4 md:grid-cols-2">
        <Card>
          <h3 className="text-sm uppercase text-zinc-400">Pas</h3>
          <div className="mt-3 h-44">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={steps.data || []}>
                <XAxis dataKey="day" hide />
                <Tooltip />
                <Line type="monotone" dataKey="steps" stroke="#34d399" strokeWidth={2} dot={false} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </Card>
      </div>
    </div>
  );
}
