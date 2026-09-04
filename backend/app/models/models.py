import uuid
from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import Uuid

from app.database.base import Base, TimestampMixin


class User(TimestampMixin, Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    first_name: Mapped[str] = mapped_column(String(80), default="")
    hashed_password: Mapped[str] = mapped_column(String(255), default="")


class Profile(TimestampMixin, Base):
    __tablename__ = "profiles"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), unique=True)
    sex: Mapped[str] = mapped_column(String(20), default="unknown")
    birth_date: Mapped[Date | None] = mapped_column(Date, nullable=True)
    height_cm: Mapped[float] = mapped_column(Float, default=0)
    current_weight_kg: Mapped[float] = mapped_column(Float, default=0)
    target_weight_kg: Mapped[float] = mapped_column(Float, default=0)
    waist_cm: Mapped[float] = mapped_column(Float, default=0)
    target_waist_cm: Mapped[float] = mapped_column(Float, default=0)
    training_frequency: Mapped[int] = mapped_column(Integer, default=4)
    physical_goal: Mapped[str] = mapped_column(String(120), default="recomposition")
    training_level: Mapped[str] = mapped_column(String(50), default="intermediate")
    dietary_preferences: Mapped[str] = mapped_column(Text, default="")
    allergies: Mapped[str] = mapped_column(Text, default="")
    forbidden_foods: Mapped[str] = mapped_column(Text, default="")
    injuries: Mapped[str] = mapped_column(Text, default="")


class Goal(TimestampMixin, Base):
    __tablename__ = "goals"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    calories_kcal: Mapped[int] = mapped_column(Integer, default=1900)
    protein_g: Mapped[int] = mapped_column(Integer, default=180)
    carbs_g: Mapped[int] = mapped_column(Integer, default=170)
    fats_g: Mapped[int] = mapped_column(Integer, default=55)
    fiber_g: Mapped[int] = mapped_column(Integer, default=30)
    water_ml: Mapped[int] = mapped_column(Integer, default=2500)
    steps: Mapped[int] = mapped_column(Integer, default=8000)


class Food(TimestampMixin, Base):
    __tablename__ = "foods"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(120), unique=True, index=True)
    default_weight_state: Mapped[str] = mapped_column(String(10), default="RAW")
    calories_per_100g: Mapped[float] = mapped_column(Float)
    protein_per_100g: Mapped[float] = mapped_column(Float)
    carbs_per_100g: Mapped[float] = mapped_column(Float)
    fats_per_100g: Mapped[float] = mapped_column(Float)
    fiber_per_100g: Mapped[float] = mapped_column(Float)


class CustomFood(TimestampMixin, Base):
    __tablename__ = "custom_foods"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    name: Mapped[str] = mapped_column(String(120), index=True)
    calories_per_100g: Mapped[float] = mapped_column(Float)
    protein_per_100g: Mapped[float] = mapped_column(Float)
    carbs_per_100g: Mapped[float] = mapped_column(Float)
    fats_per_100g: Mapped[float] = mapped_column(Float)
    fiber_per_100g: Mapped[float] = mapped_column(Float)


class Meal(TimestampMixin, Base):
    __tablename__ = "meals"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    consumed_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), index=True)
    meal_type: Mapped[str] = mapped_column(String(30), index=True)
    title: Mapped[str] = mapped_column(String(120), default="Meal")


class MealItem(TimestampMixin, Base):
    __tablename__ = "meal_items"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    meal_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("meals.id", ondelete="CASCADE"), index=True)
    food_name: Mapped[str] = mapped_column(String(120))
    weight_g: Mapped[float] = mapped_column(Float)
    weight_state: Mapped[str] = mapped_column(String(10), default="RAW")
    calories: Mapped[float] = mapped_column(Float)
    protein_g: Mapped[float] = mapped_column(Float)
    carbs_g: Mapped[float] = mapped_column(Float)
    fats_g: Mapped[float] = mapped_column(Float)
    fiber_g: Mapped[float] = mapped_column(Float)


class Recipe(TimestampMixin, Base):
    __tablename__ = "recipes"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    name: Mapped[str] = mapped_column(String(120), index=True)


class RecipeItem(TimestampMixin, Base):
    __tablename__ = "recipe_items"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    recipe_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("recipes.id", ondelete="CASCADE"), index=True)
    food_name: Mapped[str] = mapped_column(String(120))
    weight_g: Mapped[float] = mapped_column(Float)


class DailyNutrition(TimestampMixin, Base):
    __tablename__ = "daily_nutrition"
    __table_args__ = (UniqueConstraint("user_id", "day", name="uq_daily_nutrition_user_day"),)

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    day: Mapped[Date] = mapped_column(Date, index=True)
    calories: Mapped[float] = mapped_column(Float, default=0)
    protein_g: Mapped[float] = mapped_column(Float, default=0)
    carbs_g: Mapped[float] = mapped_column(Float, default=0)
    fats_g: Mapped[float] = mapped_column(Float, default=0)
    fiber_g: Mapped[float] = mapped_column(Float, default=0)
    water_ml: Mapped[float] = mapped_column(Float, default=0)


class BodyMeasurement(TimestampMixin, Base):
    __tablename__ = "body_measurements"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    day: Mapped[Date] = mapped_column(Date, index=True)
    weight_kg: Mapped[float] = mapped_column(Float)
    waist_cm: Mapped[float] = mapped_column(Float)
    chest_cm: Mapped[float] = mapped_column(Float, default=0)
    shoulders_cm: Mapped[float] = mapped_column(Float, default=0)
    arms_cm: Mapped[float] = mapped_column(Float, default=0)
    thighs_cm: Mapped[float] = mapped_column(Float, default=0)
    hips_cm: Mapped[float] = mapped_column(Float, default=0)
    body_fat_pct: Mapped[float | None] = mapped_column(Float, nullable=True)
    muscle_mass_kg: Mapped[float | None] = mapped_column(Float, nullable=True)
    body_water_pct: Mapped[float | None] = mapped_column(Float, nullable=True)


class ProgressPhoto(TimestampMixin, Base):
    __tablename__ = "progress_photos"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    day: Mapped[Date] = mapped_column(Date, index=True)
    pose: Mapped[str] = mapped_column(String(20), index=True)
    image_url: Mapped[str] = mapped_column(Text)
    weight_kg: Mapped[float | None] = mapped_column(Float, nullable=True)
    waist_cm: Mapped[float | None] = mapped_column(Float, nullable=True)


class StepLog(TimestampMixin, Base):
    __tablename__ = "step_logs"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    day: Mapped[Date] = mapped_column(Date, index=True)
    steps: Mapped[int] = mapped_column(Integer)


class SleepLog(TimestampMixin, Base):
    __tablename__ = "sleep_logs"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    day: Mapped[Date] = mapped_column(Date, index=True)
    hours: Mapped[float] = mapped_column(Float)
    quality_10: Mapped[int] = mapped_column(Integer)


class RecoveryLog(TimestampMixin, Base):
    __tablename__ = "recovery_logs"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    day: Mapped[Date] = mapped_column(Date, index=True)
    fatigue_10: Mapped[int] = mapped_column(Integer)
    soreness_10: Mapped[int] = mapped_column(Integer)
    stress_10: Mapped[int] = mapped_column(Integer)
    motivation_10: Mapped[int] = mapped_column(Integer)


pain_side_enum = Enum("left", "right", "bilateral", name="pain_side_enum")
pain_type_enum = Enum("courbature", "brulure", "tiraillement", "douleur_vive", "autre", name="pain_type_enum")


class PainLog(TimestampMixin, Base):
    __tablename__ = "pain_logs"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    recovery_log_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("recovery_logs.id", ondelete="CASCADE"), index=True)
    body_part: Mapped[str] = mapped_column(String(50), index=True)
    side: Mapped[str] = mapped_column(pain_side_enum)
    intensity_10: Mapped[int] = mapped_column(Integer)
    pain_type: Mapped[str] = mapped_column(pain_type_enum)


class WorkoutProgram(TimestampMixin, Base):
    __tablename__ = "workout_programs"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    name: Mapped[str] = mapped_column(String(120))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)


class WorkoutDay(TimestampMixin, Base):
    __tablename__ = "workout_days"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    program_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("workout_programs.id", ondelete="CASCADE"), index=True)
    weekday: Mapped[int] = mapped_column(Integer)
    split_type: Mapped[str] = mapped_column(String(30))
    title: Mapped[str] = mapped_column(String(120))


class ExerciseLibrary(TimestampMixin, Base):
    __tablename__ = "exercise_library"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(120), unique=True)
    primary_muscle: Mapped[str] = mapped_column(String(50), index=True)
    secondary_muscles: Mapped[str] = mapped_column(Text, default="")
    equipment: Mapped[str] = mapped_column(String(60), default="")
    media_url: Mapped[str] = mapped_column(Text, default="")


class Workout(TimestampMixin, Base):
    __tablename__ = "workouts"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    performed_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), index=True)
    title: Mapped[str] = mapped_column(String(120))
    split_type: Mapped[str] = mapped_column(String(30))


class WorkoutExercise(TimestampMixin, Base):
    __tablename__ = "workout_exercises"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    workout_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("workouts.id", ondelete="CASCADE"), index=True)
    exercise_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("exercise_library.id", ondelete="RESTRICT"), index=True)
    target_sets: Mapped[int] = mapped_column(Integer, default=4)
    rep_range: Mapped[str] = mapped_column(String(20), default="6-10")


class WorkoutSet(TimestampMixin, Base):
    __tablename__ = "workout_sets"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    workout_exercise_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("workout_exercises.id", ondelete="CASCADE"), index=True)
    weight_kg: Mapped[float] = mapped_column(Float)
    reps: Mapped[int] = mapped_column(Integer)
    rir: Mapped[int | None] = mapped_column(Integer, nullable=True)
    rpe: Mapped[float | None] = mapped_column(Float, nullable=True)
    is_warmup: Mapped[bool] = mapped_column(Boolean, default=False)


class AIConversation(TimestampMixin, Base):
    __tablename__ = "ai_conversations"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    title: Mapped[str] = mapped_column(String(120), default="COACH IA")


class AIMessage(TimestampMixin, Base):
    __tablename__ = "ai_messages"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    conversation_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("ai_conversations.id", ondelete="CASCADE"), index=True)
    role: Mapped[str] = mapped_column(String(20))
    content: Mapped[str] = mapped_column(Text)


class AIDailyReport(TimestampMixin, Base):
    __tablename__ = "ai_daily_reports"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    day: Mapped[Date] = mapped_column(Date, index=True)
    content: Mapped[str] = mapped_column(Text)


class AIWeeklyReport(TimestampMixin, Base):
    __tablename__ = "ai_weekly_reports"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    week_start: Mapped[Date] = mapped_column(Date, index=True)
    content: Mapped[str] = mapped_column(Text)


Index("ix_meals_user_consumed", Meal.user_id, Meal.consumed_at)
Index("ix_measurements_user_day", BodyMeasurement.user_id, BodyMeasurement.day)
Index("ix_steps_user_day", StepLog.user_id, StepLog.day)
Index("ix_workouts_user_performed", Workout.user_id, Workout.performed_at)
