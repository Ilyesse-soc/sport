from datetime import date, timedelta
from fastapi import APIRouter, Depends, File, Request, UploadFile
from sqlalchemy.orm import Session

from app.ai.provider import get_ai_provider
from app.api.dependencies.auth import get_current_user
from app.core.config import get_settings
from app.core.rate_limit import enforce_rate_limit
from app.core.upload_security import validate_and_reencode_image
from app.database.session import get_db
from app.models.models import AIDailyReport, AIMessage, AIWeeklyReport, AIConversation, User
from app.schemas.common import CoachMessageOut, CoachPromptIn, PlateEstimateOut
from app.services.coach_service import coach_answer

router = APIRouter(prefix="/coach", tags=["coach"])


@router.post("/chat", response_model=CoachMessageOut)
async def chat(payload: CoachPromptIn, request: Request, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    enforce_rate_limit(request, "ai", str(user.id))
    convo = db.query(AIConversation).filter(AIConversation.user_id == user.id).order_by(AIConversation.created_at.desc()).first()
    if not convo:
        convo = AIConversation(user_id=user.id, title="COACH IA")
        db.add(convo)
        db.flush()
    db.add(AIMessage(conversation_id=convo.id, role="user", content=payload.message))
    answer = await coach_answer(db, user.id, payload.message)
    db.add(AIMessage(conversation_id=convo.id, role="assistant", content=answer))
    db.commit()
    return CoachMessageOut(answer=answer)


@router.post("/analyze-plate", response_model=PlateEstimateOut)
async def analyze_plate(
    request: Request,
    image: UploadFile = File(...),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    _ = db
    enforce_rate_limit(request, "ai_photo", str(user.id))
    settings = get_settings()
    data = await image.read()
    clean_image, clean_mime, _object_key = validate_and_reencode_image(
        data,
        image.content_type or "",
        settings.max_upload_size_mb * 1024 * 1024,
    )

    prompt = (
        "Tu es un estimateur nutritionnel prudent."
        " Liste les aliments visibles, portions estimees, kcal/proteines/glucides/lipides/fibres"
        " avec une plage d'incertitude, jamais en valeur unique."
    )
    provider = get_ai_provider()
    result = await provider.vision_estimate(clean_image, clean_mime, prompt)
    return PlateEstimateOut.model_validate(result)


@router.post("/daily-report")
async def generate_daily_report(request: Request, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    enforce_rate_limit(request, "ai", str(user.id))
    content = await coach_answer(db, user.id, "Genere mon bilan journalier concis.")
    row = AIDailyReport(user_id=user.id, day=date.today(), content=content)
    db.add(row)
    db.commit()
    return {"content": content}


@router.post("/weekly-report")
async def generate_weekly_report(request: Request, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    enforce_rate_limit(request, "ai", str(user.id))
    content = await coach_answer(db, user.id, "Genere mon bilan hebdomadaire concis.")
    week_start = date.today() - timedelta(days=6)
    row = AIWeeklyReport(user_id=user.id, week_start=week_start, content=content)
    db.add(row)
    db.commit()
    return {"content": content}
