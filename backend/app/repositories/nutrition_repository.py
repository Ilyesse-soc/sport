from datetime import date
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.models import Meal


def get_meals_by_day(db: Session, user_id, day: date):
    return (
        db.query(Meal)
        .filter(Meal.user_id == user_id)
        .filter(func.date(Meal.consumed_at) == day)
        .order_by(Meal.consumed_at.asc())
        .all()
    )
