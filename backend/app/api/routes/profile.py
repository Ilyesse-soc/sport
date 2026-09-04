from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from app.api.dependencies.auth import get_current_user
from app.core.rate_limit import enforce_rate_limit
from app.database.session import get_db
from app.models.models import (
    AIConversation,
    AIDailyReport,
    AIMessage,
    AIWeeklyReport,
    BodyMeasurement,
    Goal,
    Meal,
    MealItem,
    PainLog,
    Profile,
    ProgressPhoto,
    RecoveryLog,
    SleepLog,
    StepLog,
    User,
    Workout,
    WorkoutExercise,
    WorkoutProgram,
    WorkoutSet,
)
from app.schemas.common import GoalIn, GoalOut, ProfileIn, ProfileOut

router = APIRouter(prefix="/profile", tags=["profile"])


@router.get("", response_model=ProfileOut)
def get_profile(
    request: Request,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    enforce_rate_limit(request, "api", str(user.id))
    profile = db.query(Profile).filter(Profile.user_id == user.id).first()
    if not profile:
        profile = Profile(user_id=user.id)
        db.add(profile)
        db.commit()
        db.refresh(profile)
    return ProfileOut(
        user_id=user.id,
        first_name=user.first_name,
        sex=profile.sex,
        birth_date=profile.birth_date,
        height_cm=profile.height_cm,
        current_weight_kg=profile.current_weight_kg,
        target_weight_kg=profile.target_weight_kg,
        waist_cm=profile.waist_cm,
        target_waist_cm=profile.target_waist_cm,
        training_frequency=profile.training_frequency,
        physical_goal=profile.physical_goal,
        training_level=profile.training_level,
        dietary_preferences=profile.dietary_preferences,
        allergies=profile.allergies,
        forbidden_foods=profile.forbidden_foods,
        injuries=profile.injuries,
    )


@router.put("", response_model=ProfileOut)
def update_profile(
    payload: ProfileIn,
    request: Request,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    enforce_rate_limit(request, "api", str(user.id))
    profile = db.query(Profile).filter(Profile.user_id == user.id).first()
    if not profile:
        profile = Profile(user_id=user.id)
        db.add(profile)
    user.first_name = payload.first_name
    profile.sex = payload.sex
    profile.birth_date = payload.birth_date
    profile.height_cm = payload.height_cm
    profile.current_weight_kg = payload.current_weight_kg
    profile.target_weight_kg = payload.target_weight_kg
    profile.waist_cm = payload.waist_cm
    profile.target_waist_cm = payload.target_waist_cm
    profile.training_frequency = payload.training_frequency
    profile.physical_goal = payload.physical_goal
    profile.training_level = payload.training_level
    profile.dietary_preferences = payload.dietary_preferences
    profile.allergies = payload.allergies
    profile.forbidden_foods = payload.forbidden_foods
    profile.injuries = payload.injuries
    db.commit()
    db.refresh(profile)
    return ProfileOut(user_id=user.id, first_name=user.first_name, **payload.model_dump())


@router.get("/goals", response_model=GoalOut)
def get_goals(request: Request, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    enforce_rate_limit(request, "api", str(user.id))
    goal = db.query(Goal).filter(Goal.user_id == user.id).first()
    if not goal:
        goal = Goal(user_id=user.id)
        db.add(goal)
        db.commit()
        db.refresh(goal)
    return GoalOut.model_validate(goal, from_attributes=True)


@router.put("/goals", response_model=GoalOut)
def update_goals(payload: GoalIn, request: Request, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    enforce_rate_limit(request, "api", str(user.id))
    goal = db.query(Goal).filter(Goal.user_id == user.id).first()
    if not goal:
        goal = Goal(user_id=user.id)
        db.add(goal)
    for key, value in payload.model_dump().items():
        setattr(goal, key, value)
    db.commit()
    db.refresh(goal)
    return GoalOut.model_validate(goal, from_attributes=True)


@router.get("/export")
def export_my_data(request: Request, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    enforce_rate_limit(request, "api", str(user.id))
    meals = db.query(Meal).filter(Meal.user_id == user.id).all()
    meal_ids = [m.id for m in meals]
    profile = db.query(Profile).filter(Profile.user_id == user.id).first()
    goals = db.query(Goal).filter(Goal.user_id == user.id).first()
    return {
        "user": {"id": str(user.id), "email": user.email, "first_name": user.first_name},
        "profile": {
            "sex": profile.sex,
            "birth_date": profile.birth_date.isoformat() if profile and profile.birth_date else None,
            "height_cm": profile.height_cm,
            "current_weight_kg": profile.current_weight_kg,
            "target_weight_kg": profile.target_weight_kg,
            "waist_cm": profile.waist_cm,
            "target_waist_cm": profile.target_waist_cm,
            "training_frequency": profile.training_frequency,
            "physical_goal": profile.physical_goal,
            "training_level": profile.training_level,
            "dietary_preferences": profile.dietary_preferences,
            "allergies": profile.allergies,
            "forbidden_foods": profile.forbidden_foods,
            "injuries": profile.injuries,
        } if profile else None,
        "goals": {
            "calories_kcal": goals.calories_kcal,
            "protein_g": goals.protein_g,
            "carbs_g": goals.carbs_g,
            "fats_g": goals.fats_g,
            "fiber_g": goals.fiber_g,
            "water_ml": goals.water_ml,
            "steps": goals.steps,
        } if goals else None,
        "meals": [{"id": str(m.id), "meal_type": m.meal_type, "title": m.title, "consumed_at": m.consumed_at.isoformat()} for m in meals],
        "meal_items": [{"id": str(i.id), "meal_id": str(i.meal_id), "food_name": i.food_name} for i in db.query(MealItem).filter(MealItem.meal_id.in_(meal_ids)).all()] if meal_ids else [],
        "measurements": [{"id": str(x.id), "day": x.day.isoformat(), "weight_kg": x.weight_kg} for x in db.query(BodyMeasurement).filter(BodyMeasurement.user_id == user.id).all()],
        "photos": [{"id": str(x.id), "pose": x.pose, "day": x.day.isoformat(), "image_url": x.image_url} for x in db.query(ProgressPhoto).filter(ProgressPhoto.user_id == user.id).all()],
        "steps": [{"id": str(x.id), "day": x.day.isoformat(), "steps": x.steps} for x in db.query(StepLog).filter(StepLog.user_id == user.id).all()],
        "sleep": [{"id": str(x.id), "day": x.day.isoformat(), "hours": x.hours} for x in db.query(SleepLog).filter(SleepLog.user_id == user.id).all()],
        "recovery": [{"id": str(x.id), "day": x.day.isoformat()} for x in db.query(RecoveryLog).filter(RecoveryLog.user_id == user.id).all()],
        "pain": [{"id": str(x.id), "body_part": x.body_part, "intensity_10": x.intensity_10} for x in db.query(PainLog).join(RecoveryLog, RecoveryLog.id == PainLog.recovery_log_id).filter(RecoveryLog.user_id == user.id).all()],
        "workouts": [{"id": str(x.id), "title": x.title, "performed_at": x.performed_at.isoformat()} for x in db.query(Workout).filter(Workout.user_id == user.id).all()],
    }


@router.delete("/account")
def delete_my_account(request: Request, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    enforce_rate_limit(request, "api", str(user.id))
    meal_ids = [x.id for x in db.query(Meal).filter(Meal.user_id == user.id).all()]
    if meal_ids:
        db.query(MealItem).filter(MealItem.meal_id.in_(meal_ids)).delete(synchronize_session=False)
    workout_ids = [x.id for x in db.query(Workout).filter(Workout.user_id == user.id).all()]
    if workout_ids:
        workout_ex_ids = [x.id for x in db.query(WorkoutExercise).filter(WorkoutExercise.workout_id.in_(workout_ids)).all()]
        if workout_ex_ids:
            db.query(WorkoutSet).filter(WorkoutSet.workout_exercise_id.in_(workout_ex_ids)).delete(synchronize_session=False)
        db.query(WorkoutExercise).filter(WorkoutExercise.workout_id.in_(workout_ids)).delete(synchronize_session=False)
        db.query(Workout).filter(Workout.id.in_(workout_ids)).delete(synchronize_session=False)
    recovery_ids = [x.id for x in db.query(RecoveryLog).filter(RecoveryLog.user_id == user.id).all()]
    if recovery_ids:
        db.query(PainLog).filter(PainLog.recovery_log_id.in_(recovery_ids)).delete(synchronize_session=False)
    db.query(RecoveryLog).filter(RecoveryLog.user_id == user.id).delete(synchronize_session=False)
    db.query(SleepLog).filter(SleepLog.user_id == user.id).delete(synchronize_session=False)
    db.query(StepLog).filter(StepLog.user_id == user.id).delete(synchronize_session=False)
    db.query(ProgressPhoto).filter(ProgressPhoto.user_id == user.id).delete(synchronize_session=False)
    db.query(BodyMeasurement).filter(BodyMeasurement.user_id == user.id).delete(synchronize_session=False)
    db.query(Meal).filter(Meal.user_id == user.id).delete(synchronize_session=False)
    db.query(Goal).filter(Goal.user_id == user.id).delete(synchronize_session=False)
    db.query(Profile).filter(Profile.user_id == user.id).delete(synchronize_session=False)
    conv_ids = [x.id for x in db.query(AIConversation).filter(AIConversation.user_id == user.id).all()]
    if conv_ids:
        db.query(AIMessage).filter(AIMessage.conversation_id.in_(conv_ids)).delete(synchronize_session=False)
    db.query(AIConversation).filter(AIConversation.user_id == user.id).delete(synchronize_session=False)
    db.query(AIDailyReport).filter(AIDailyReport.user_id == user.id).delete(synchronize_session=False)
    db.query(AIWeeklyReport).filter(AIWeeklyReport.user_id == user.id).delete(synchronize_session=False)
    db.query(WorkoutProgram).filter(WorkoutProgram.user_id == user.id).delete(synchronize_session=False)
    db.delete(user)
    db.commit()
    return {"message": "Compte supprime. Pense a supprimer les objets storage associes."}
