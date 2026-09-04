from datetime import date, datetime, timedelta, timezone

from app.database.session import SessionLocal, engine
from app.database.base import Base
from app.models.models import (
    BodyMeasurement,
    ExerciseLibrary,
    Food,
    Goal,
    Meal,
    MealItem,
    Profile,
    StepLog,
    User,
    Workout,
    WorkoutDay,
    WorkoutProgram,
)
from app.core.security import hash_password


def run_seed() -> None:
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        if db.query(User).filter(User.email == "demo@sport.app").first():
            return

        demo = User(email="demo@sport.app", first_name="Demo", hashed_password=hash_password("demo1234"))
        db.add(demo)
        db.flush()

        db.add(
            Profile(
                user_id=demo.id,
                sex="male",
                height_cm=185,
                current_weight_kg=97,
                target_weight_kg=88,
                waist_cm=91.4,
                target_waist_cm=83.8,
                training_frequency=5,
                physical_goal="fat_loss_with_muscle_retention",
                training_level="intermediate",
            )
        )
        db.add(
            Goal(
                user_id=demo.id,
                calories_kcal=1900,
                protein_g=180,
                carbs_g=170,
                fats_g=55,
                fiber_g=30,
                water_ml=2800,
                steps=9000,
            )
        )

        foods = [
            Food(name="Riz basmati cru", default_weight_state="RAW", calories_per_100g=358, protein_per_100g=7, carbs_per_100g=78, fats_per_100g=0.8, fiber_per_100g=1.2),
            Food(name="Blanc de poulet cru", default_weight_state="RAW", calories_per_100g=114, protein_per_100g=23, carbs_per_100g=0, fats_per_100g=1.6, fiber_per_100g=0),
            Food(name="Flocons d'avoine", default_weight_state="RAW", calories_per_100g=368, protein_per_100g=13, carbs_per_100g=59, fats_per_100g=7, fiber_per_100g=10),
            Food(name="Pomme de terre crue", default_weight_state="RAW", calories_per_100g=77, protein_per_100g=2, carbs_per_100g=17, fats_per_100g=0.1, fiber_per_100g=2.2),
            Food(name="Saumon cru", default_weight_state="RAW", calories_per_100g=208, protein_per_100g=20, carbs_per_100g=0, fats_per_100g=13, fiber_per_100g=0),
        ]
        db.add_all(foods)

        for i in range(30):
            d = date.today() - timedelta(days=29 - i)
            db.add(
                BodyMeasurement(
                    user_id=demo.id,
                    day=d,
                    weight_kg=97 - (i * 0.03),
                    waist_cm=91.4 - (i * 0.02),
                    chest_cm=109,
                )
            )
            db.add(StepLog(user_id=demo.id, day=d, steps=7000 + ((i * 241) % 3000)))

        now = datetime.now(timezone.utc)
        meal = Meal(user_id=demo.id, meal_type="dejeuner", title="Poulet riz", consumed_at=now)
        db.add(meal)
        db.flush()
        db.add_all(
            [
                MealItem(meal_id=meal.id, food_name="Riz basmati cru", weight_g=60, weight_state="RAW", calories=215, protein_g=4.2, carbs_g=46.8, fats_g=0.5, fiber_g=0.7),
                MealItem(meal_id=meal.id, food_name="Blanc de poulet cru", weight_g=180, weight_state="RAW", calories=205, protein_g=41.4, carbs_g=0, fats_g=2.9, fiber_g=0),
            ]
        )

        ex = [
            ExerciseLibrary(name="Developpe incline halteres", primary_muscle="pectoraux", secondary_muscles="deltoides anterieurs,triceps", equipment="halteres"),
            ExerciseLibrary(name="Tractions pronation", primary_muscle="dorsaux", secondary_muscles="biceps", equipment="barre"),
            ExerciseLibrary(name="Squat", primary_muscle="quadriceps", secondary_muscles="fessiers,ischios", equipment="barre"),
        ]
        db.add_all(ex)
        db.flush()

        program = WorkoutProgram(user_id=demo.id, name="Demo Push Pull Legs", is_active=True)
        db.add(program)
        db.flush()
        split = [
            (0, "Push"), (1, "Pull"), (2, "Legs + Abs"), (3, "Repos"), (4, "Upper V-Taper"), (5, "Legs + Shoulders + Abs"), (6, "Repos")
        ]
        for wd, title in split:
            db.add(WorkoutDay(program_id=program.id, weekday=wd, split_type=title, title=title))

        db.add(Workout(user_id=demo.id, title="Upper", split_type="Upper", performed_at=now - timedelta(days=1)))

        db.commit()
    finally:
        db.close()


if __name__ == "__main__":
    run_seed()
