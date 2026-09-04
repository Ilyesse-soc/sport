from datetime import date
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.api.dependencies.auth import get_current_user
from app.core.config import get_settings
from app.core.rate_limit import enforce_rate_limit
from app.database.session import get_db
from app.models.models import DailyNutrition, Food, Meal, MealItem, User
from app.schemas.common import DailySummaryOut, MealIn, MealOut

router = APIRouter(prefix="/nutrition", tags=["nutrition"])


@router.get("/foods")
def search_foods(
    request: Request,
    q: str = Query(default="", max_length=120),
    limit: int = Query(default=25, ge=1, le=100),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    enforce_rate_limit(request, "api", str(user.id))
    _ = user
    query = db.query(Food)
    if q:
        query = query.filter(Food.name.ilike(f"%{q}%"))
    rows = query.order_by(Food.name.asc()).limit(limit).all()
    return [
        {
            "id": str(f.id),
            "name": f.name,
            "default_weight_state": f.default_weight_state,
            "calories_per_100g": f.calories_per_100g,
            "protein_per_100g": f.protein_per_100g,
            "carbs_per_100g": f.carbs_per_100g,
            "fats_per_100g": f.fats_per_100g,
            "fiber_per_100g": f.fiber_per_100g,
        }
        for f in rows
    ]


@router.post("/meals", response_model=MealOut)
def add_meal(payload: MealIn, request: Request, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    enforce_rate_limit(request, "api", str(user.id))

    meal = Meal(user_id=user.id, meal_type=payload.meal_type, title=payload.title, consumed_at=payload.consumed_at)
    db.add(meal)
    db.flush()
    calories = protein = carbs = fats = fiber = 0.0
    for item in payload.items:
        db.add(
            MealItem(
                meal_id=meal.id,
                food_name=item.food_name,
                weight_g=item.weight_g,
                weight_state=item.weight_state,
                calories=item.calories,
                protein_g=item.protein_g,
                carbs_g=item.carbs_g,
                fats_g=item.fats_g,
                fiber_g=item.fiber_g,
            )
        )
        calories += item.calories
        protein += item.protein_g
        carbs += item.carbs_g
        fats += item.fats_g
        fiber += item.fiber_g

    day = payload.consumed_at.date()
    daily = db.query(DailyNutrition).filter(DailyNutrition.user_id == user.id, DailyNutrition.day == day).first()
    if not daily:
        daily = DailyNutrition(
            user_id=user.id,
            day=day,
            calories=0,
            protein_g=0,
            carbs_g=0,
            fats_g=0,
            fiber_g=0,
            water_ml=0,
        )
        db.add(daily)
    daily.calories += calories
    daily.protein_g += protein
    daily.carbs_g += carbs
    daily.fats_g += fats
    daily.fiber_g += fiber

    db.commit()
    db.refresh(meal)
    return MealOut(
        id=meal.id,
        meal_type=meal.meal_type,
        title=meal.title,
        consumed_at=meal.consumed_at,
        calories=calories,
        protein_g=protein,
        carbs_g=carbs,
        fats_g=fats,
        fiber_g=fiber,
    )


@router.get("/meals")
def list_meals(
    request: Request,
    day: date,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    enforce_rate_limit(request, "api", str(user.id))
    max_page_size = get_settings().max_page_size
    page_size = min(page_size, max_page_size)
    offset = (page - 1) * page_size
    rows = (
        db.query(Meal)
        .filter(Meal.user_id == user.id)
        .filter(func.date(Meal.consumed_at) == day)
        .order_by(Meal.consumed_at.asc())
        .offset(offset)
        .limit(page_size)
        .all()
    )
    return [{"id": str(m.id), "meal_type": m.meal_type, "title": m.title, "consumed_at": m.consumed_at.isoformat()} for m in rows]


@router.get("/meals/{meal_id}")
def get_meal(meal_id: UUID, request: Request, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    enforce_rate_limit(request, "api", str(user.id))
    meal = db.query(Meal).filter(Meal.id == meal_id, Meal.user_id == user.id).first()
    if not meal:
        raise HTTPException(status_code=404, detail="Meal not found")
    items = db.query(MealItem).filter(MealItem.meal_id == meal.id).all()
    return {
        "id": str(meal.id),
        "meal_type": meal.meal_type,
        "title": meal.title,
        "consumed_at": meal.consumed_at.isoformat(),
        "items": [
            {
                "id": str(i.id),
                "food_name": i.food_name,
                "weight_g": i.weight_g,
                "weight_state": i.weight_state,
                "calories": i.calories,
                "protein_g": i.protein_g,
                "carbs_g": i.carbs_g,
                "fats_g": i.fats_g,
                "fiber_g": i.fiber_g,
            }
            for i in items
        ],
    }


@router.get("/daily-summary", response_model=DailySummaryOut)
def daily_summary(day: date, request: Request, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    enforce_rate_limit(request, "api", str(user.id))
    row = db.query(DailyNutrition).filter(DailyNutrition.user_id == user.id, DailyNutrition.day == day).first()
    if not row:
        return DailySummaryOut(day=day, calories=0, protein_g=0, carbs_g=0, fats_g=0, fiber_g=0, water_ml=0)
    return DailySummaryOut.model_validate(row, from_attributes=True)
