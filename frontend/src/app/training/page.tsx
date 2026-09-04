"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Card } from "@/components/ui/card";
import { SectionTitle } from "@/components/ui/section-title";
import { apiGet, apiPost } from "@/services/api";

type Exercise = { id: string; name: string; primary_muscle: string };
type Workout = { id: string; title: string; split_type: string; performed_at: string };
type Volume = { muscle: string; sets: number };

export default function TrainingPage() {
  const queryClient = useQueryClient();
  const exercises = useQuery({ queryKey: ["exercises"], queryFn: () => apiGet<Exercise[]>("/training/exercises") });
  const workouts = useQuery({ queryKey: ["workouts"], queryFn: () => apiGet<Workout[]>("/training/workouts") });
  const volume = useQuery({ queryKey: ["volume"], queryFn: () => apiGet<Volume[]>("/training/volume") });

  const addWorkout = useMutation({
    mutationFn: async () => {
      const firstExercise = exercises.data?.[0];
      if (!firstExercise) return;
      return apiPost("/training/workouts", {
        title: "Upper Session",
        split_type: "Upper",
        performed_at: new Date().toISOString(),
        exercises: [
          {
            exercise_id: firstExercise.id,
            target_sets: 4,
            rep_range: "6-10",
            sets: [
              { weight_kg: 30, reps: 8, rir: 2, rpe: 8, is_warmup: false },
              { weight_kg: 30, reps: 8, rir: 2, rpe: 8, is_warmup: false },
              { weight_kg: 30, reps: 7, rir: 1, rpe: 9, is_warmup: false },
            ],
          },
        ],
      });
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["workouts"] });
      queryClient.invalidateQueries({ queryKey: ["volume"] });
    },
  });

  return (
    <div className="space-y-5">
      <SectionTitle title="Training" subtitle="Progressive overload et volume par groupe musculaire" />

      <Card className="space-y-3">
        <h3 className="text-base font-semibold">Nouvelle seance</h3>
        <button className="rounded-xl bg-cyan-500 px-4 py-2 text-sm font-semibold text-slate-950" onClick={() => addWorkout.mutate()}>
          Ajouter seance demo
        </button>
      </Card>

      <Card>
        <h3 className="text-base font-semibold">Dernieres seances</h3>
        <div className="mt-3 space-y-2 text-sm text-zinc-300">
          {(workouts.data || []).slice(0, 8).map((w) => (
            <div key={w.id} className="rounded-lg border border-white/10 px-3 py-2">
              {w.title} - {w.split_type}
            </div>
          ))}
        </div>
      </Card>

      <Card>
        <h3 className="text-base font-semibold">Volume hebdo</h3>
        <div className="mt-3 grid gap-2 text-sm text-zinc-300">
          {(volume.data || []).map((v) => (
            <div key={v.muscle} className="flex justify-between rounded-lg border border-white/10 px-3 py-2">
              <span>{v.muscle}</span>
              <span>{v.sets} series</span>
            </div>
          ))}
        </div>
      </Card>
    </div>
  );
}
