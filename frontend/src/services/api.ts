const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL || "";
const USE_LOCAL_MODE = process.env.NEXT_PUBLIC_LOCAL_MODE !== "0";
const DB_KEY = "sport_local_db_v1";

type Food = { id: string; name: string; calories_per_100g: number };
type MealItem = {
  food_name: string;
  weight_g: number;
  calories: number;
  protein_g: number;
  carbs_g: number;
  fats_g: number;
  fiber_g: number;
};
type Meal = { id: string; day: string; meal_type: string; title: string; consumed_at: string; items: MealItem[] };
type Exercise = { id: string; name: string; primary_muscle: string };
type WorkoutSet = { weight_kg: number; reps: number; rir: number; rpe: number; is_warmup: boolean };
type WorkoutExercise = { exercise_id: string; target_sets: number; rep_range: string; sets: WorkoutSet[] };
type Workout = { id: string; title: string; split_type: string; performed_at: string; exercises: WorkoutExercise[] };
type Measurement = { id: string; day: string; weight_kg: number; waist_cm: number; chest_cm: number };
type StepEntry = { day: string; steps: number };
type RecoveryJournal = {
  day: string;
  hours_sleep: number;
  quality_10: number;
  fatigue_10: number;
  soreness_10: number;
  stress_10: number;
  motivation_10: number;
};
type Profile = {
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
type Goal = {
  calories_kcal: number;
  protein_g: number;
  carbs_g: number;
  fats_g: number;
  fiber_g: number;
  water_ml: number;
  steps: number;
};
type LocalDb = {
  users: { id: string; email: string; password: string; first_name: string }[];
  profile: Profile;
  goals: Goal;
  foods: Food[];
  meals: Meal[];
  exercises: Exercise[];
  workouts: Workout[];
  measurements: Measurement[];
  steps: StepEntry[];
  recoveryJournals: RecoveryJournal[];
};

function getAuthHeaders(): HeadersInit {
  if (typeof window === "undefined") {
    return {};
  }
  const token = window.localStorage.getItem("sport_token");
  if (!token) {
    return {};
  }
  return { Authorization: `Bearer ${token}` };
}

function jsonHeaders(): HeadersInit {
  return {
    "Content-Type": "application/json",
    ...getAuthHeaders(),
  };
}

function createId(): string {
  if (typeof crypto !== "undefined" && "randomUUID" in crypto) {
    return crypto.randomUUID();
  }
  return `${Date.now()}-${Math.random().toString(16).slice(2)}`;
}

function defaultDb(): LocalDb {
  const today = new Date().toISOString().slice(0, 10);
  return {
    users: [{ id: "demo-user", email: "demo@sport.app", password: "demo123456", first_name: "Demo" }],
    profile: {
      first_name: "Demo",
      sex: "male",
      birth_date: null,
      height_cm: 181,
      current_weight_kg: 97,
      target_weight_kg: 88,
      waist_cm: 92,
      target_waist_cm: 84,
      training_frequency: 4,
      physical_goal: "recomposition",
      training_level: "intermediate",
      dietary_preferences: "",
      allergies: "",
      forbidden_foods: "",
      injuries: "",
    },
    goals: {
      calories_kcal: 2600,
      protein_g: 180,
      carbs_g: 280,
      fats_g: 75,
      fiber_g: 30,
      water_ml: 3000,
      steps: 9000,
    },
    foods: [
      { id: "food-1", name: "Riz basmati cru", calories_per_100g: 358 },
      { id: "food-2", name: "Poulet blanc", calories_per_100g: 120 },
      { id: "food-3", name: "Avoine", calories_per_100g: 389 },
    ],
    meals: [
      {
        id: "meal-1",
        day: today,
        meal_type: "dejeuner",
        title: "Repas demo",
        consumed_at: new Date().toISOString(),
        items: [
          { food_name: "Riz basmati cru", weight_g: 60, calories: 215, protein_g: 4.2, carbs_g: 46.8, fats_g: 0.5, fiber_g: 0.7 },
        ],
      },
    ],
    exercises: [
      { id: "ex-1", name: "Developpe couche", primary_muscle: "Pectoraux" },
      { id: "ex-2", name: "Tractions", primary_muscle: "Dos" },
      { id: "ex-3", name: "Squat", primary_muscle: "Quadriceps" },
    ],
    workouts: [],
    measurements: [{ id: "m-1", day: today, weight_kg: 97, waist_cm: 92, chest_cm: 108 }],
    steps: [{ day: today, steps: 7600 }],
    recoveryJournals: [],
  };
}

function loadDb(): LocalDb {
  if (typeof window === "undefined") {
    return defaultDb();
  }
  const raw = window.localStorage.getItem(DB_KEY);
  if (!raw) {
    const seed = defaultDb();
    window.localStorage.setItem(DB_KEY, JSON.stringify(seed));
    return seed;
  }
  try {
    return JSON.parse(raw) as LocalDb;
  } catch {
    const seed = defaultDb();
    window.localStorage.setItem(DB_KEY, JSON.stringify(seed));
    return seed;
  }
}

function saveDb(db: LocalDb): void {
  if (typeof window === "undefined") {
    return;
  }
  window.localStorage.setItem(DB_KEY, JSON.stringify(db));
}

function getQueryParam(path: string, key: string): string {
  const search = path.includes("?") ? path.slice(path.indexOf("?")) : "";
  const params = new URLSearchParams(search);
  return params.get(key) || "";
}

function asRecord(payload: unknown): Record<string, unknown> {
  if (payload && typeof payload === "object") {
    return payload as Record<string, unknown>;
  }
  return {};
}

function localGet<T>(path: string): T {
  const db = loadDb();
  if (path === "/profile") return db.profile as T;
  if (path === "/profile/goals") return db.goals as T;
  if (path === "/nutrition/foods") return db.foods as T;
  if (path.startsWith("/nutrition/meals")) {
    const day = getQueryParam(path, "day");
    const rows = day ? db.meals.filter((m) => m.day === day) : db.meals;
    return rows as T;
  }
  if (path.startsWith("/nutrition/daily-summary")) {
    const day = getQueryParam(path, "day");
    const meals = db.meals.filter((m) => !day || m.day === day);
    const summary = meals.flatMap((m) => m.items).reduce(
      (acc, item) => {
        acc.calories += item.calories;
        acc.protein_g += item.protein_g;
        acc.carbs_g += item.carbs_g;
        acc.fats_g += item.fats_g;
        acc.fiber_g += item.fiber_g;
        return acc;
      },
      { day: day || new Date().toISOString().slice(0, 10), calories: 0, protein_g: 0, carbs_g: 0, fats_g: 0, fiber_g: 0, water_ml: 0 },
    );
    return summary as T;
  }
  if (path === "/training/exercises") return db.exercises as T;
  if (path === "/training/workouts") {
    const rows = [...db.workouts].sort((a, b) => b.performed_at.localeCompare(a.performed_at));
    return rows as T;
  }
  if (path === "/training/volume") {
    const byId = new Map(db.exercises.map((e) => [e.id, e.primary_muscle]));
    const map = new Map<string, number>();
    for (const w of db.workouts) {
      for (const ex of w.exercises) {
        const muscle = byId.get(ex.exercise_id) || "Autre";
        const current = map.get(muscle) || 0;
        map.set(muscle, current + ex.sets.filter((s) => !s.is_warmup).length);
      }
    }
    return Array.from(map.entries()).map(([muscle, sets]) => ({ muscle, sets })) as T;
  }
  if (path === "/progression/measurements") return db.measurements as T;
  if (path === "/recovery/steps") return db.steps as T;
  if (path === "/recovery/status") {
    const latest = db.recoveryJournals[db.recoveryJournals.length - 1];
    if (!latest) return { score: 70 } as T;
    const score = Math.max(
      0,
      Math.min(
        100,
        Math.round(
          latest.hours_sleep * 8 + latest.quality_10 * 4 - latest.fatigue_10 * 3 - latest.soreness_10 * 2 - latest.stress_10 * 2 + latest.motivation_10 * 2,
        ),
      ),
    );
    return { score } as T;
  }
  throw new Error(`Route GET locale non supportee: ${path}`);
}

function localPost<T>(path: string, payload: unknown): T {
  const body = asRecord(payload);
  const db = loadDb();
  if (path === "/auth/login") {
    const user = db.users.find((u) => u.email.toLowerCase() === String(body.email || "").toLowerCase());
    if (!user || user.password !== String(body.password || "")) {
      throw new Error("Invalid credentials");
    }
    return { access_token: `local-token-${user.id}`, token_type: "bearer", user_id: user.id } as T;
  }
  if (path === "/auth/register") {
    const email = String(body.email || "").toLowerCase().trim();
    if (!email || !body.password) throw new Error("Invalid payload");
    if (db.users.some((u) => u.email === email)) throw new Error("Email already exists");
    const id = createId();
    db.users.push({ id, email, password: String(body.password), first_name: String(body.first_name || "") });
    db.profile.first_name = String(body.first_name || "Demo");
    saveDb(db);
    return { access_token: `local-token-${id}`, token_type: "bearer", user_id: id } as T;
  }
  if (path === "/nutrition/meals") {
    const consumedAt = String(body.consumed_at || new Date().toISOString());
    const meal: Meal = {
      id: createId(),
      day: consumedAt.slice(0, 10),
      meal_type: String(body.meal_type || "repas"),
      title: String(body.title || "Repas"),
      consumed_at: consumedAt,
      items: Array.isArray(body.items) ? (body.items as MealItem[]) : [],
    };
    db.meals.push(meal);
    saveDb(db);
    return meal as T;
  }
  if (path === "/training/workouts") {
    const workout: Workout = {
      id: createId(),
      title: String(body.title || "Workout"),
      split_type: String(body.split_type || "Full body"),
      performed_at: String(body.performed_at || new Date().toISOString()),
      exercises: Array.isArray(body.exercises) ? (body.exercises as WorkoutExercise[]) : [],
    };
    db.workouts.push(workout);
    saveDb(db);
    return workout as T;
  }
  if (path === "/progression/measurements") {
    const m: Measurement = {
      id: createId(),
      day: String(body.day || new Date().toISOString().slice(0, 10)),
      weight_kg: Number(body.weight_kg || 0),
      waist_cm: Number(body.waist_cm || 0),
      chest_cm: Number(body.chest_cm || 0),
    };
    db.measurements.push(m);
    saveDb(db);
    return m as T;
  }
  if (path === "/recovery/steps") {
    const s: StepEntry = { day: String(body.day), steps: Number(body.steps || 0) };
    db.steps.push(s);
    saveDb(db);
    return s as T;
  }
  if (path === "/recovery/journal") {
    const j: RecoveryJournal = {
      day: String(body.day),
      hours_sleep: Number(body.hours_sleep || 0),
      quality_10: Number(body.quality_10 || 0),
      fatigue_10: Number(body.fatigue_10 || 0),
      soreness_10: Number(body.soreness_10 || 0),
      stress_10: Number(body.stress_10 || 0),
      motivation_10: Number(body.motivation_10 || 0),
    };
    db.recoveryJournals.push(j);
    saveDb(db);
    return j as T;
  }
  if (path === "/coach/chat") {
    const text = String(body.message || "").toLowerCase();
    const answer = text.includes("analyse")
      ? "Aujourd'hui: reste hydraté, vise ton quota proteines et garde 1-2 reps en reserve sur les mouvements lourds."
      : "Continue sur cette dynamique: regularite, surcharge progressive et sommeil stable."
    return { answer } as T;
  }
  throw new Error(`Route POST locale non supportee: ${path}`);
}

function localPut<T>(path: string, payload: unknown): T {
  const body = asRecord(payload);
  const db = loadDb();
  if (path === "/profile") {
    db.profile = { ...db.profile, ...body };
    saveDb(db);
    return db.profile as T;
  }
  throw new Error(`Route PUT locale non supportee: ${path}`);
}

function localUpload<T>(path: string, file: File): T {
  if (path === "/coach/analyze-plate") {
    return {
      confidence: "moyenne",
      disclaimer: "Estimation locale sans IA distante. Ajuste les quantites manuellement.",
      items: [{ raw_response: `Fichier recu: ${file.name}. Suggestion: source proteinee + feculents + legumes.` }],
    } as T;
  }
  throw new Error(`Route UPLOAD locale non supportee: ${path}`);
}

export async function apiGet<T>(path: string): Promise<T> {
  if (USE_LOCAL_MODE) {
    return localGet<T>(path);
  }
  const response = await fetch(`${API_BASE}${path}`, { headers: jsonHeaders(), cache: "no-store" });
  if (!response.ok) throw new Error(await response.text());
  return (await response.json()) as T;
}

export async function apiPost<T>(path: string, payload: unknown): Promise<T> {
  if (USE_LOCAL_MODE) {
    return localPost<T>(path, payload);
  }
  const response = await fetch(`${API_BASE}${path}`, {
    method: "POST",
    headers: jsonHeaders(),
    body: JSON.stringify(payload),
  });
  if (!response.ok) throw new Error(await response.text());
  return (await response.json()) as T;
}

export async function apiPut<T>(path: string, payload: unknown): Promise<T> {
  if (USE_LOCAL_MODE) {
    return localPut<T>(path, payload);
  }
  const response = await fetch(`${API_BASE}${path}`, {
    method: "PUT",
    headers: jsonHeaders(),
    body: JSON.stringify(payload),
  });
  if (!response.ok) throw new Error(await response.text());
  return (await response.json()) as T;
}

export async function apiUpload<T>(path: string, file: File): Promise<T> {
  if (USE_LOCAL_MODE) {
    return localUpload<T>(path, file);
  }
  const form = new FormData();
  form.append("image", file);
  const response = await fetch(`${API_BASE}${path}`, {
    method: "POST",
    headers: getAuthHeaders(),
    body: form,
  });
  if (!response.ok) throw new Error(await response.text());
  return (await response.json()) as T;
}
