from sqlalchemy.orm import Session

from app.models.models import Workout


def get_recent_workouts(db: Session, user_id, limit: int = 10):
    return (
        db.query(Workout)
        .filter(Workout.user_id == user_id)
        .order_by(Workout.performed_at.desc())
        .limit(limit)
        .all()
    )
