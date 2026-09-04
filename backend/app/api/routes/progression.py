from datetime import date
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from app.api.dependencies.auth import get_current_user
from app.core.rate_limit import enforce_rate_limit
from app.database.session import get_db
from app.models.models import BodyMeasurement, ProgressPhoto, User
from app.schemas.common import MeasurementIn

router = APIRouter(prefix="/progression", tags=["progression"])


@router.post("/measurements")
def add_measurement(payload: MeasurementIn, request: Request, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    enforce_rate_limit(request, "api", str(user.id))
    row = BodyMeasurement(
        user_id=user.id,
        day=payload.day,
        weight_kg=payload.weight_kg,
        waist_cm=payload.waist_cm,
        chest_cm=payload.chest_cm,
        shoulders_cm=payload.shoulders_cm,
        arms_cm=payload.arms_cm,
        thighs_cm=payload.thighs_cm,
        hips_cm=payload.hips_cm,
        body_fat_pct=payload.body_fat_pct,
        muscle_mass_kg=payload.muscle_mass_kg,
        body_water_pct=payload.body_water_pct,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return {"id": str(row.id)}


@router.get("/measurements")
def list_measurements(request: Request, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    enforce_rate_limit(request, "api", str(user.id))
    rows = (
        db.query(BodyMeasurement)
        .filter(BodyMeasurement.user_id == user.id)
        .order_by(BodyMeasurement.day.asc())
        .all()
    )
    return [
        {
            "id": str(r.id),
            "day": r.day.isoformat(),
            "weight_kg": r.weight_kg,
            "waist_cm": r.waist_cm,
            "chest_cm": r.chest_cm,
            "ratio_chest_waist": round((r.chest_cm / r.waist_cm), 2) if r.waist_cm else None,
        }
        for r in rows
    ]


@router.get("/measurements/{measurement_id}")
def get_measurement(measurement_id: UUID, request: Request, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    enforce_rate_limit(request, "api", str(user.id))
    row = db.query(BodyMeasurement).filter(BodyMeasurement.id == measurement_id, BodyMeasurement.user_id == user.id).first()
    if not row:
        raise HTTPException(status_code=404, detail="Measurement not found")
    return {
        "id": str(row.id),
        "day": row.day.isoformat(),
        "weight_kg": row.weight_kg,
        "waist_cm": row.waist_cm,
        "chest_cm": row.chest_cm,
    }


@router.post("/photos")
def add_photo(
    pose: str,
    image_url: str,
    day: str,
    request: Request,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    enforce_rate_limit(request, "upload", str(user.id))
    row = ProgressPhoto(user_id=user.id, pose=pose, image_url=image_url, day=date.fromisoformat(day))
    db.add(row)
    db.commit()
    db.refresh(row)
    return {"id": str(row.id)}


@router.get("/photos")
def list_photos(request: Request, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    enforce_rate_limit(request, "api", str(user.id))
    rows = db.query(ProgressPhoto).filter(ProgressPhoto.user_id == user.id).order_by(ProgressPhoto.day.desc()).all()
    return [{"id": str(r.id), "pose": r.pose, "image_url": r.image_url, "day": r.day.isoformat()} for r in rows]


@router.get("/photos/{photo_id}")
def get_photo(photo_id: UUID, request: Request, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    enforce_rate_limit(request, "api", str(user.id))
    row = db.query(ProgressPhoto).filter(ProgressPhoto.id == photo_id, ProgressPhoto.user_id == user.id).first()
    if not row:
        raise HTTPException(status_code=404, detail="Photo not found")
    return {"id": str(row.id), "pose": row.pose, "image_url": row.image_url, "day": row.day.isoformat()}
