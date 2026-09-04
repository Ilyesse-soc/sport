from datetime import date, datetime
from uuid import UUID
from pydantic import BaseModel, Field
from typing import Literal


class MessageResponse(BaseModel):
    message: str


class GoalOut(BaseModel):
    calories_kcal: int
    protein_g: int
    carbs_g: int
    fats_g: int
    fiber_g: int
    water_ml: int
    steps: int


class ProfileIn(BaseModel):
    first_name: str = Field(default="", max_length=80)
    sex: Literal["male", "female", "other", "unknown"] = "unknown"
    birth_date: date | None = None
    height_cm: float = Field(default=170, ge=100, le=250, allow_inf_nan=False)
    current_weight_kg: float = Field(default=70, ge=30, le=400, allow_inf_nan=False)
    target_weight_kg: float = Field(default=70, ge=30, le=400, allow_inf_nan=False)
    waist_cm: float = Field(default=80, ge=30, le=250, allow_inf_nan=False)
    target_waist_cm: float = Field(default=75, ge=30, le=250, allow_inf_nan=False)
    training_frequency: int = Field(default=4, ge=0, le=14)
    physical_goal: str = Field(default="recomposition", max_length=120)
    training_level: str = Field(default="intermediate", max_length=50)
    dietary_preferences: str = Field(default="", max_length=5000)
    allergies: str = Field(default="", max_length=5000)
    forbidden_foods: str = Field(default="", max_length=5000)
    injuries: str = Field(default="", max_length=5000)


class GoalIn(BaseModel):
    calories_kcal: int = Field(default=1900, ge=0, le=15000)
    protein_g: int = Field(default=180, ge=0, le=1000)
    carbs_g: int = Field(default=170, ge=0, le=1500)
    fats_g: int = Field(default=55, ge=0, le=800)
    fiber_g: int = Field(default=30, ge=0, le=300)
    water_ml: int = Field(default=2500, ge=0, le=10000)
    steps: int = Field(default=8000, ge=0, le=100000)


class ProfileOut(ProfileIn):
    user_id: UUID


class MealItemIn(BaseModel):
    food_name: str = Field(max_length=150)
    weight_g: float = Field(gt=0, le=5000, allow_inf_nan=False)
    weight_state: Literal["RAW", "COOKED"] = "RAW"
    calories: float = Field(ge=0, le=5000, allow_inf_nan=False)
    protein_g: float = Field(ge=0, le=1000, allow_inf_nan=False)
    carbs_g: float = Field(ge=0, le=1000, allow_inf_nan=False)
    fats_g: float = Field(ge=0, le=1000, allow_inf_nan=False)
    fiber_g: float = Field(ge=0, le=300, allow_inf_nan=False)


class MealIn(BaseModel):
    meal_type: Literal["petit_dejeuner", "dejeuner", "diner", "snack", "pre_entrainement", "post_entrainement"]
    title: str = Field(max_length=120)
    consumed_at: datetime
    items: list[MealItemIn] = Field(min_length=1, max_length=50)


class MealOut(BaseModel):
    id: UUID
    meal_type: str
    title: str
    consumed_at: datetime
    calories: float
    protein_g: float
    carbs_g: float
    fats_g: float
    fiber_g: float


class DailySummaryOut(BaseModel):
    day: date
    calories: float
    protein_g: float
    carbs_g: float
    fats_g: float
    fiber_g: float
    water_ml: float


class MeasurementIn(BaseModel):
    day: date
    weight_kg: float = Field(ge=30, le=400, allow_inf_nan=False)
    waist_cm: float = Field(ge=30, le=250, allow_inf_nan=False)
    chest_cm: float = Field(default=0, ge=0, le=300, allow_inf_nan=False)
    shoulders_cm: float = Field(default=0, ge=0, le=300, allow_inf_nan=False)
    arms_cm: float = Field(default=0, ge=0, le=150, allow_inf_nan=False)
    thighs_cm: float = Field(default=0, ge=0, le=200, allow_inf_nan=False)
    hips_cm: float = Field(default=0, ge=0, le=250, allow_inf_nan=False)
    body_fat_pct: float | None = Field(default=None, ge=0, le=100, allow_inf_nan=False)
    muscle_mass_kg: float | None = Field(default=None, ge=0, le=250, allow_inf_nan=False)
    body_water_pct: float | None = Field(default=None, ge=0, le=100, allow_inf_nan=False)


class StepLogIn(BaseModel):
    day: date
    steps: int = Field(ge=0, le=100000)


class RecoveryIn(BaseModel):
    day: date
    hours_sleep: float = Field(ge=0, le=24, allow_inf_nan=False)
    quality_10: int = Field(ge=0, le=10)
    fatigue_10: int = Field(ge=0, le=10)
    soreness_10: int = Field(ge=0, le=10)
    stress_10: int = Field(ge=0, le=10)
    motivation_10: int = Field(ge=0, le=10)


class PainIn(BaseModel):
    body_part: str = Field(max_length=50)
    side: Literal["left", "right", "bilateral"]
    intensity_10: int = Field(ge=0, le=10)
    pain_type: Literal["courbature", "brulure", "tiraillement", "douleur_vive", "autre"]


class WorkoutSetIn(BaseModel):
    weight_kg: float = Field(ge=0, le=1000, allow_inf_nan=False)
    reps: int = Field(ge=0, le=200)
    rir: int | None = Field(default=None, ge=0, le=10)
    rpe: float | None = Field(default=None, ge=0, le=10, allow_inf_nan=False)
    is_warmup: bool = False


class WorkoutExerciseIn(BaseModel):
    exercise_id: UUID
    target_sets: int = Field(default=4, ge=1, le=20)
    rep_range: str = Field(default="6-10", max_length=20)
    sets: list[WorkoutSetIn] = Field(min_length=1, max_length=30)


class WorkoutIn(BaseModel):
    title: str = Field(max_length=120)
    split_type: str = Field(max_length=30)
    performed_at: datetime
    exercises: list[WorkoutExerciseIn] = Field(min_length=1, max_length=25)


class CoachPromptIn(BaseModel):
    message: str = Field(min_length=1, max_length=4000)


class CoachMessageOut(BaseModel):
    answer: str


class PlateEstimateOut(BaseModel):
    confidence: str
    disclaimer: str
    items: list[dict]
