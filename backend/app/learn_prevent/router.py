import uuid
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.shared.database import get_db
from app.shared.auth import get_current_user
from app.shared.models import User, SafetyTip, QuizQuestion, QuizOption, Article

router = APIRouter()


class QuizAnswerSubmission(BaseModel):
    question_id: str
    selected_option_id: str


@router.get("/daily-tip")
async def get_daily_tip(db: AsyncSession = Depends(get_db)):
    stmt = select(SafetyTip).where(SafetyTip.is_active == True).limit(1)
    result = await db.execute(stmt)
    tip = result.scalar_one_or_none()
    
    if not tip:
        return {
            "tip_id": str(uuid.uuid4()),
            "tip_text": "Never share OTPs or UPI PINs with anyone — not even bank officials. Genuine banks will never ask for your PIN or OTP over a call.",
            "category": "otp_security",
            "date": "2026-08-20"
        }

    return {
        "tip_id": str(tip.id),
        "tip_text": tip.tip_text,
        "category": tip.category,
        "date": "2026-08-20"
    }


@router.get("/quiz")
async def get_quiz_questions(count: int = 10, current_user: User = Depends(get_current_user)):
    # Sample quiz questions fulfilling FR-087
    questions = [
        {
            "question_id": "q-001",
            "question_text": "A caller claiming to be from your bank asks for your UPI PIN to 'verify your account'. What should you do?",
            "category": "upi_fraud",
            "options": [
                {"option_id": "o-1", "text": "Share the PIN — it is your bank calling"},
                {"option_id": "o-2", "text": "Hang up immediately and contact your bank via their official number"},
                {"option_id": "o-3", "text": "Ask them to send an SMS verification code"},
                {"option_id": "o-4", "text": "Share only the last 2 digits"}
            ]
        },
        {
            "question_id": "q-002",
            "question_text": "You receive a WhatsApp message from an unknown number claiming your electricity will be disconnected tonight unless you click a link. Is this genuine?",
            "category": "whatsapp_scam",
            "options": [
                {"option_id": "o-5", "text": "Yes, utility companies send urgent messages on WhatsApp"},
                {"option_id": "o-6", "text": "No, this is a classic urgency scam. Official bills are paid via official apps/portals"},
                {"option_id": "o-7", "text": "Yes, but only if they include a discount code"}
            ]
        }
    ]
    return {"quiz_id": str(uuid.uuid4()), "questions": questions}


@router.post("/quiz/submit-answer")
async def submit_quiz_answer(payload: QuizAnswerSubmission, current_user: User = Depends(get_current_user)):
    is_correct = payload.selected_option_id in ["o-2", "o-6"]
    
    explanations = {
        "q-001": "Genuine banks and financial institutions will never ask for your UPI PIN, password, or OTP over a call.",
        "q-002": "Utility boards do not send disconnection threats with unknown bitly links via WhatsApp. Always check bills on official portals."
    }

    return {
        "is_correct": is_correct,
        "correct_option_id": "o-2" if payload.question_id == "q-001" else "o-6",
        "explanation": explanations.get(payload.question_id, "Always verify urgent claims through official channels.")
    }


@router.get("/articles")
async def list_articles(category: Optional[str] = None):
    articles = [
        {
            "id": "art-001",
            "title": "Understanding UPI Collect Request Fraud & How to Stay Safe",
            "slug": "upi-collect-fraud-guide",
            "category": "upi_fraud",
            "summary": "Learn how fraudsters trick users into entering UPI PINs for receiving money."
        },
        {
            "id": "art-002",
            "title": "WhatsApp KYC & Account Block Scams Explained",
            "slug": "whatsapp-kyc-scams",
            "category": "whatsapp_scam",
            "summary": "Recognize fake bank advisories and fraudulent link messages on WhatsApp."
        }
    ]
    return {"articles": articles}


@router.get("/articles/{slug}")
async def get_article(slug: str):
    return {
        "title": "Understanding UPI Collect Request Fraud & How to Stay Safe",
        "slug": slug,
        "content": "# UPI Collect Request Scams\n\nRemember: Entering your UPI PIN **deducts** money from your account. You NEVER need to enter a UPI PIN to **receive** money.",
        "category": "upi_fraud",
        "published_at": "2026-08-15T10:00:00Z"
    }
