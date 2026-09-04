"use client";

import { useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";
import { Card } from "@/components/ui/card";
import { SectionTitle } from "@/components/ui/section-title";
import { apiGet, apiPost, apiUpload } from "@/services/api";

type MealRow = { id: string; meal_type: string; title: string; consumed_at: string };
type FoodRow = { id: string; name: string; calories_per_100g: number };

export default function NutritionPage() {
  const today = new Date().toISOString().slice(0, 10);
  const queryClient = useQueryClient();
  const [photo, setPhoto] = useState<File | null>(null);
  const meals = useQuery({ queryKey: ["meals", today], queryFn: () => apiGet<MealRow[]>(`/nutrition/meals?day=${today}`) });
  const foods = useQuery({ queryKey: ["foods"], queryFn: () => apiGet<FoodRow[]>("/nutrition/foods") });

  const addMeal = useMutation({
    mutationFn: () =>
      apiPost("/nutrition/meals", {
        meal_type: "dejeuner",
        title: "Repas rapide",
        consumed_at: new Date().toISOString(),
        items: [
          {
            food_name: "Riz basmati cru",
            weight_g: 60,
            weight_state: "RAW",
            calories: 215,
            protein_g: 4.2,
            carbs_g: 46.8,
            fats_g: 0.5,
            fiber_g: 0.7,
          },
        ],
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["meals", today] });
      queryClient.invalidateQueries({ queryKey: ["summary", today] });
      toast.success("Repas ajoute");
    },
    onError: () => toast.error("Echec ajout repas"),
  });

  const analyzePlate = useMutation({
    mutationFn: async () => {
      if (!photo) throw new Error("Aucune photo");
      return apiUpload<{ confidence: string; disclaimer: string; items: { raw_response?: string }[] }>("/coach/analyze-plate", photo);
    },
  });

  return (
    <div className="space-y-5">
      <SectionTitle title="Nutrition" subtitle="Poids cru supporte pour les aliments" />

      <Card className="space-y-3">
        <h3 className="text-base font-semibold">Ajouter un repas</h3>
        <button
          className="rounded-xl bg-cyan-500 px-4 py-2 text-sm font-semibold text-slate-950"
          onClick={() => addMeal.mutate()}
        >
          Ajouter repas demo (riz cru 60g)
        </button>
      </Card>

      <Card className="space-y-2">
        <h3 className="text-base font-semibold">Analyser mon assiette</h3>
        <input type="file" accept="image/png,image/jpeg,image/webp" onChange={(e) => setPhoto(e.target.files?.[0] || null)} />
        <button className="rounded-xl bg-emerald-400 px-4 py-2 text-sm font-semibold text-slate-950" onClick={() => analyzePlate.mutate()}>
          Lancer analyse IA
        </button>
        {analyzePlate.data ? (
          <div className="rounded-lg border border-amber-300/30 bg-amber-300/10 p-3 text-sm text-amber-100">
            <p>Confiance: {analyzePlate.data.confidence}</p>
            <p>{analyzePlate.data.disclaimer}</p>
            <pre className="mt-2 whitespace-pre-wrap text-xs">{analyzePlate.data.items?.[0]?.raw_response || "Ajuste les quantites avant sauvegarde."}</pre>
          </div>
        ) : null}
      </Card>

      <Card>
        <h3 className="text-base font-semibold">Aliments</h3>
        <div className="mt-3 space-y-2 text-sm text-zinc-300">
          {(foods.data || []).slice(0, 12).map((food) => (
            <div key={food.id} className="flex justify-between rounded-lg border border-white/10 px-3 py-2">
              <span>{food.name}</span>
              <span>{food.calories_per_100g} kcal / 100g</span>
            </div>
          ))}
        </div>
      </Card>

      <Card>
        <h3 className="text-base font-semibold">Repas du jour</h3>
        <div className="mt-3 space-y-2 text-sm text-zinc-300">
          {(meals.data || []).map((meal) => (
            <div key={meal.id} className="rounded-lg border border-white/10 px-3 py-2">
              {meal.title} - {meal.meal_type}
            </div>
          ))}
        </div>
      </Card>
    </div>
  );
}
