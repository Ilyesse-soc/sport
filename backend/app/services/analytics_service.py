from datetime import date, datetime, timedelta
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.models import (
    BodyMeasurement,
    DailyNutrition,
    Goal,
    Meal,
    MealItem,
    RecoveryLog,
    SleepLog,
    StepLog,
    Workout,
    WorkoutExercise,
    WorkoutSet,
)


def get_today_nutrition(db: Session, user_id, day: date) -> dict:
    row = (
        db.query(
            func.coalesce(func.sum(MealItem.calories), 0.0),
            func.coalesce(func.sum(MealItem.protein_g), 0.0),
            func.coalesce(func.sum(MealItem.carbs_g), 0.0),
            func.coalesce(func.sum(MealItem.fats_g), 0.0),
            func.coalesce(func.sum(MealItem.fiber_g), 0.0),
        )
        .join(Meal, Meal.id == MealItem.meal_id)
        .filter(Meal.user_id == user_id)
        .filter(func.date(Meal.consumed_at) == day)
        .one()
    )
    return {
        "calories": float(row[0]),
        "protein_g": float(row[1]),
        "carbs_g": float(row[2]),
        "fats_g": float(row[3]),
        "fiber_g": float(row[4]),
    }


def get_nutrition_history(db: Session, user_id, days: int = 30) -> list[dict]:
    start = date.today() - timedelta(days=days - 1)
    rows = (
        db.query(DailyNutrition)
        .filter(DailyNutrition.user_id == user_id)
        .filter(DailyNutrition.day >= start)
        .order_by(DailyNutrition.day.asc())
        .all()
    )
    return [
        {
            "day": r.day.isoformat(),
            "calories": r.calories,
            "protein_g": r.protein_g,
            "carbs_g": r.carbs_g,
            "fats_g": r.fats_g,
            "fiber_g": r.fiber_g,
            "water_ml": r.water_ml,
        }
        for r in rows
    ]


def get_weight_history(db: Session, user_id, days: int = 30) -> list[dict]:
    start = date.today() - timedelta(days=days - 1)
    rows = (
        db.query(BodyMeasurement)
        .filter(BodyMeasurement.user_id == user_id)
        .filter(BodyMeasurement.day >= start)
        .order_by(BodyMeasurement.day.asc())
        .all()
    )
    return [{"day": r.day.isoformat(), "weight_kg": r.weight_kg, "waist_cm": r.waist_cm} for r in rows]


def get_measurements(db: Session, user_id) -> list[dict]:
    rows = (
        db.query(BodyMeasurement)
        .filter(BodyMeasurement.user_id == user_id)
        .order_by(BodyMeasurement.day.desc())
        .limit(30)
        .all()
    )
    return [
        {
            "day": r.day.isoformat(),
            "weight_kg": r.weight_kg,
            "waist_cm": r.waist_cm,
            "chest_cm": r.chest_cm,
        }
        for r in rows
    ]


def get_workout_history(db: Session, user_id, days: int = 60) -> list[dict]:
    start_dt = datetime.utcnow() - timedelta(days=days)
    rows = (
        db.query(Workout)
        .filter(Workout.user_id == user_id)
        .filter(Workout.performed_at >= start_dt)
        .order_by(Workout.performed_at.desc())
        .all()
    )
    return [{"id": str(w.id), "title": w.title, "split_type": w.split_type, "performed_at": w.performed_at.isoformat()} for w in rows]


def get_exercise_progress(db: Session, user_id, exercise_id) -> list[dict]:
    rows = (
        db.query(WorkoutSet.weight_kg, WorkoutSet.reps, Workout.performed_at)
        .join(WorkoutExercise, WorkoutExercise.id == WorkoutSet.workout_exercise_id)
        .join(Workout, Workout.id == WorkoutExercise.workout_id)
        .filter(Workout.user_id == user_id)
        .filter(WorkoutExercise.exercise_id == exercise_id)
        .order_by(Workout.performed_at.desc())
        .limit(50)
        .all()
    )
    return [{"weight_kg": float(r[0]), "reps": int(r[1]), "performed_at": r[2].isoformat()} for r in rows]


def get_recovery_status(db: Session, user_id) -> dict:
    last_recovery = (
        db.query(RecoveryLog)
        .filter(RecoveryLog.user_id == user_id)
        .order_by(RecoveryLog.day.desc())
        .first()
    )
    last_sleep = (
        db.query(SleepLog)
        .filter(SleepLog.user_id == user_id)
        .order_by(SleepLog.day.desc())
        .first()
    )
    if not last_recovery:
        return {"score": 0, "note": "Aucune donnee de recuperation."}
    score = max(0, min(100, int((last_recovery.motivation_10 * 10) + (10 - last_recovery.fatigue_10) * 5)))
    return {
        "score": score,
        "sleep_hours": last_sleep.hours if last_sleep else None,
        "fatigue_10": last_recovery.fatigue_10,
        "soreness_10": last_recovery.soreness_10,
        "stress_10": last_recovery.stress_10,
    }


def get_step_history(db: Session, user_id, days: int = 14) -> list[dict]:
    start = date.today() - timedelta(days=days - 1)
    rows = (
        db.query(StepLog)
        .filter(StepLog.user_id == user_id)
        .filter(StepLog.day >= start)
        .order_by(StepLog.day.asc())
        .all()
    )
    return [{"day": s.day.isoformat(), "steps": s.steps} for s in rows]


def get_goals(db: Session, user_id) -> Goal | None:
    return db.query(Goal).filter(Goal.user_id == user_id).first()
