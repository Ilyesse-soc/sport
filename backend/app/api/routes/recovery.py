from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from app.api.dependencies.auth import get_current_user
from app.core.rate_limit import enforce_rate_limit
from app.database.session import get_db
from app.models.models import PainLog, RecoveryLog, SleepLog, StepLog, User
from app.schemas.common import PainIn, RecoveryIn, StepLogIn

router = APIRouter(prefix="/recovery", tags=["recovery"])


@router.post("/steps")
def add_steps(payload: StepLogIn, request: Request, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    enforce_rate_limit(request, "api", str(user.id))
    row = StepLog(user_id=user.id, day=payload.day, steps=payload.steps)
    db.add(row)
    db.commit()
    return {"ok": True}


@router.get("/steps")
def list_steps(request: Request, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    enforce_rate_limit(request, "api", str(user.id))
    rows = db.query(StepLog).filter(StepLog.user_id == user.id).order_by(StepLog.day.asc()).all()
    return [{"day": s.day.isoformat(), "steps": s.steps} for s in rows]


@router.post("/journal")
def add_recovery(
    payload: RecoveryIn,
    request: Request,
    pains: list[PainIn] | None = None,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    enforce_rate_limit(request, "api", str(user.id))
    sleep = SleepLog(user_id=user.id, day=payload.day, hours=payload.hours_sleep, quality_10=payload.quality_10)
    recovery = RecoveryLog(
        user_id=user.id,
        day=payload.day,
        fatigue_10=payload.fatigue_10,
        soreness_10=payload.soreness_10,
        stress_10=payload.stress_10,
        motivation_10=payload.motivation_10,
    )
    db.add(sleep)
    db.add(recovery)
    db.flush()

    for pain in pains or []:
        db.add(PainLog(recovery_log_id=recovery.id, **pain.model_dump()))
    db.commit()
    return {
        "ok": True,
        "medical_notice": "Si douleur vive, persistante ou inhabituelle, consulte un professionnel de sante.",
    }


@router.get("/status")
def recovery_status(request: Request, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    enforce_rate_limit(request, "api", str(user.id))
    row = db.query(RecoveryLog).filter(RecoveryLog.user_id == user.id).order_by(RecoveryLog.day.desc()).first()
    if not row:
        return {"score": 0}
    score = max(0, min(100, int((10 - row.fatigue_10) * 6 + (10 - row.stress_10) * 4 + row.motivation_10 * 4)))
    return {"score": score, "fatigue_10": row.fatigue_10, "stress_10": row.stress_10}
