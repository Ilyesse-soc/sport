export type Goal = {
  calories_kcal: number;
  protein_g: number;
  carbs_g: number;
  fats_g: number;
  fiber_g: number;
  water_ml: number;
  steps: number;
};

export type DailySummary = {
  day: string;
  calories: number;
  protein_g: number;
  carbs_g: number;
  fats_g: number;
  fiber_g: number;
  water_ml: number;
};

export type WorkoutVolume = {
  muscle: string;
  sets: number;
};

export type Measurement = {
  id: string;
  day: string;
  weight_kg: number;
  waist_cm: number;
  chest_cm: number;
  ratio_chest_waist: number | null;
};
