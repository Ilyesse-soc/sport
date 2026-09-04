from collections import defaultdict
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.orm import Session

from app.api.dependencies.auth import get_current_user
from app.core.rate_limit import enforce_rate_limit
from app.database.session import get_db
from app.models.models import ExerciseLibrary, User, Workout, WorkoutExercise, WorkoutSet
from app.schemas.common import WorkoutIn, WorkoutSetIn
from app.services.overload_service import recommend_overload

router = APIRouter(prefix="/training", tags=["training"])


@router.get("/exercises")
def list_exercises(
    request: Request,
    q: str = Query(default="", max_length=120),
    limit: int = Query(default=100, ge=1, le=100),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    enforce_rate_limit(request, "api", str(user.id))
    _ = user
    query = db.query(ExerciseLibrary)
    if q:
        query = query.filter(ExerciseLibrary.name.ilike(f"%{q}%"))
    rows = query.order_by(ExerciseLibrary.name.asc()).limit(limit).all()
    return [
        {
            "id": str(e.id),
            "name": e.name,
            "primary_muscle": e.primary_muscle,
            "secondary_muscles": e.secondary_muscles,
            "equipment": e.equipment,
        }
        for e in rows
    ]


@router.post("/workouts")
def add_workout(payload: WorkoutIn, request: Request, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    enforce_rate_limit(request, "api", str(user.id))
    workout = Workout(user_id=user.id, title=payload.title, split_type=payload.split_type, performed_at=payload.performed_at)
    db.add(workout)
    db.flush()
    for ex in payload.exercises:
        wex = WorkoutExercise(
            workout_id=workout.id,
            exercise_id=ex.exercise_id,
            target_sets=ex.target_sets,
            rep_range=ex.rep_range,
        )
        db.add(wex)
        db.flush()
        for s in ex.sets:
            db.add(WorkoutSet(workout_exercise_id=wex.id, **s.model_dump()))
    db.commit()
    return {"id": str(workout.id)}


@router.get("/workouts")
def list_workouts(
    request: Request,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    enforce_rate_limit(request, "api", str(user.id))
    offset = (page - 1) * page_size
    rows = (
        db.query(Workout)
        .filter(Workout.user_id == user.id)
        .order_by(Workout.performed_at.desc())
        .offset(offset)
        .limit(page_size)
        .all()
    )
    return [{"id": str(w.id), "title": w.title, "performed_at": w.performed_at.isoformat(), "split_type": w.split_type} for w in rows]


@router.get("/workouts/{workout_id}")
def get_workout(workout_id: UUID, request: Request, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    enforce_rate_limit(request, "api", str(user.id))
    workout = db.query(Workout).filter(Workout.id == workout_id, Workout.user_id == user.id).first()
    if not workout:
        raise HTTPException(status_code=404, detail="Workout not found")
    wex_rows = db.query(WorkoutExercise).filter(WorkoutExercise.workout_id == workout.id).all()
    details = []
    for ex in wex_rows:
        sets = db.query(WorkoutSet).filter(WorkoutSet.workout_exercise_id == ex.id).all()
        details.append(
            {
                "exercise_id": str(ex.exercise_id),
                "target_sets": ex.target_sets,
                "rep_range": ex.rep_range,
                "sets": [
                    {
                        "id": str(s.id),
                        "weight_kg": s.weight_kg,
                        "reps": s.reps,
                        "rir": s.rir,
                        "rpe": s.rpe,
                        "is_warmup": s.is_warmup,
                    }
                    for s in sets
                ],
            }
        )
    return {
        "id": str(workout.id),
        "title": workout.title,
        "split_type": workout.split_type,
        "performed_at": workout.performed_at.isoformat(),
        "exercises": details,
    }


@router.get("/volume")
def weekly_volume(request: Request, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    enforce_rate_limit(request, "api", str(user.id))
    rows = (
        db.query(ExerciseLibrary.primary_muscle, WorkoutSet.id)
        .join(WorkoutExercise, WorkoutExercise.exercise_id == ExerciseLibrary.id)
        .join(WorkoutSet, WorkoutSet.workout_exercise_id == WorkoutExercise.id)
        .join(Workout, Workout.id == WorkoutExercise.workout_id)
        .filter(Workout.user_id == user.id)
        .all()
    )
    volume = defaultdict(int)
    for muscle, _ in rows:
        volume[muscle] += 1
    return [{"muscle": muscle, "sets": sets} for muscle, sets in sorted(volume.items())]


@router.post("/overload-recommendation")
def overload_reco(
    request: Request,
    target_sets: int = Query(ge=1, le=20),
    rep_min: int = Query(ge=1, le=100),
    rep_max: int = Query(ge=1, le=100),
    current_weight: float = Query(ge=0, le=1000),
    sets: list[WorkoutSetIn] | None = None,
    user: User = Depends(get_current_user),
):
    enforce_rate_limit(request, "api", str(user.id))
    set_rows = [s.model_dump() for s in (sets or [])]
    return {"recommendation": recommend_overload(target_sets, rep_min, rep_max, set_rows, current_weight)}
