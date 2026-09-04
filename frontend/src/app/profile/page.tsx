"use client";

import { useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Card } from "@/components/ui/card";
import { SectionTitle } from "@/components/ui/section-title";
import { apiGet, apiPut } from "@/services/api";

type ProfileDto = {
  first_name: string;
  sex: string;
  birth_date: string | null;
  height_cm: number;
  current_weight_kg: number;
  target_weight_kg: number;
  waist_cm: number;
  target_waist_cm: number;
  training_frequency: number;
  physical_goal: string;
  training_level: string;
  dietary_preferences: string;
  allergies: string;
  forbidden_foods: string;
  injuries: string;
};

export default function ProfilePage() {
  const queryClient = useQueryClient();
  const profileQuery = useQuery({ queryKey: ["profile"], queryFn: () => apiGet<ProfileDto>("/profile") });
  const [firstName, setFirstName] = useState("Demo");

  const save = useMutation({
    mutationFn: async () => {
      const current = profileQuery.data;
      if (!current) return;
      return apiPut("/profile", { ...current, first_name: firstName });
    },
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["profile"] }),
  });

  return (
    <div className="space-y-5">
      <SectionTitle title="Profil" subtitle="Objectifs et donnees personnelles" />
      <Card className="space-y-3">
        <label className="text-sm text-zinc-300">Prenom</label>
        <input
          className="w-full rounded-xl border border-white/10 bg-black/30 px-3 py-2"
          value={firstName}
          onChange={(e) => setFirstName(e.target.value)}
        />
        <button className="rounded-xl bg-cyan-500 px-4 py-2 text-sm font-semibold text-slate-950" onClick={() => save.mutate()}>
          Sauvegarder
        </button>
      </Card>
    </div>
  );
}
