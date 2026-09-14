import logging
import os
from typing import Optional

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from cocare import process_message
from database.db_helper import fetch_all


# ============================================================
# Logging
# ============================================================

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("cocare-api")


# ============================================================
# FastAPI Application
# ============================================================

app = FastAPI(
    title="CoCare Backend API",
    description=(
        "Backend API for the CoCare intelligent telecom "
        "customer service prototype."
    ),
    version="1.0.0",
)


# ============================================================
# CORS
# ============================================================
#
# For the academic prototype, CORS origins can be configured
# through the CORS_ORIGINS environment variable.
#
# Example:
# CORS_ORIGINS=http://localhost:8501,http://localhost:3000
#

cors_origins = os.getenv(
    "CORS_ORIGINS",
    "http://localhost:8501",
).split(",")

cors_origins = [
    origin.strip()
    for origin in cors_origins
    if origin.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


# ============================================================
# Request / Response Models
# ============================================================

class ChatRequest(BaseModel):
    user_id: str = Field(
        ...,
        min_length=1,
        max_length=100,
        examples=["customer_1"],
    )

    message: str = Field(
        ...,
        min_length=1,
        max_length=2000,
        examples=["My internet is very slow"],
    )

    region: str = Field(
        ...,
        min_length=1,
        max_length=100,
        examples=["Amman"],
    )


class ChatResponse(BaseModel):
    language: Optional[str] = None

    intent: Optional[str] = None
    intent_confidence: Optional[float] = None

    sentiment: Optional[str] = None
    sentiment_score: Optional[float] = None

    prediction: Optional[int] = None

    response: Optional[str] = None
    followup_response: Optional[str] = None

    issue_type: Optional[str] = None

    network_problem: Optional[bool] = None

    notification_type: Optional[str] = None
    display_channel: Optional[str] = None

    escalation: Optional[bool] = None
    reason: Optional[str] = None

    repeat_count: Optional[int] = None
    area_issue_count: Optional[int] = None

    external_message_ar: Optional[str] = None
    external_message_en: Optional[str] = None

    internal_message_ar: Optional[str] = None
    internal_message_en: Optional[str] = None

    priority: Optional[str] = None
    suggested_action: Optional[str] = None
    show_to_customer: Optional[int] = None

    user_id: Optional[str] = None
    region: Optional[str] = None


# ============================================================
# Basic Routes
# ============================================================

@app.get("/")
def home():
    return {
        "app": "CoCare Backend API",
        "version": "1.0.0",
        "status": "running",
    }


@app.get("/health")
def health():
    return {
        "status": "healthy",
        "service": "cocare-backend",
    }


# ============================================================
# Customer Chat API
# ============================================================

@app.post(
    "/chat",
    response_model=ChatResponse,
)
def chat(req: ChatRequest):

    message = req.message.strip()

    if not message:
        raise HTTPException(
            status_code=400,
            detail="Message cannot be empty.",
        )

    try:
        result = process_message(
            user_message=message,
            user_id=req.user_id.strip(),
            region=req.region.strip(),
        )

        if not isinstance(result, dict):
            logger.error(
                "process_message returned an invalid response."
            )

            raise HTTPException(
                status_code=500,
                detail="Unable to process the message.",
            )

        return result

    except HTTPException:
        raise

    except Exception:
        logger.exception(
            "Unexpected error while processing chat message."
        )

        raise HTTPException(
            status_code=500,
            detail=(
                "An internal error occurred while processing "
                "the request."
            ),
        )


# ============================================================
# Employee Dashboard APIs
# ============================================================

@app.get("/chat-logs")
def get_chat_logs(
    limit: int = Query(
        default=100,
        ge=1,
        le=500,
    )
):
    try:
        rows = fetch_all(
            """
            SELECT *
            FROM chat_logs
            ORDER BY id DESC
            LIMIT ?
            """,
            (limit,),
        )

        logs = [
            dict(row)
            for row in rows
        ]

        return {
            "count": len(logs),
            "logs": logs,
        }

    except Exception:
        logger.exception(
            "Unable to retrieve chat logs."
        )

        raise HTTPException(
            status_code=500,
            detail="Unable to retrieve chat logs.",
        )


@app.get("/alerts")
def get_alerts():
    try:
        rows = fetch_all(
            """
            SELECT *
            FROM chat_logs
            WHERE network_problem = 1
               OR escalation = 1
               OR (
                    notification_type IS NOT NULL
                    AND notification_type != 'none'
               )
            ORDER BY id DESC
            LIMIT 100
            """
        )

        alerts = [
            dict(row)
            for row in rows
        ]

        return {
            "count": len(alerts),
            "alerts": alerts,
        }

    except Exception:
        logger.exception(
            "Unable to retrieve alerts."
        )

        raise HTTPException(
            status_code=500,
            detail="Unable to retrieve alerts.",
        )


@app.get("/stats")
def get_stats():
    try:
        total_messages = fetch_all(
            """
            SELECT COUNT(*) AS total
            FROM chat_logs
            """
        )[0]["total"]

        network_issues = fetch_all(
            """
            SELECT COUNT(*) AS total
            FROM chat_logs
            WHERE network_problem = 1
            """
        )[0]["total"]

        escalations = fetch_all(
            """
            SELECT COUNT(*) AS total
            FROM chat_logs
            WHERE escalation = 1
            """
        )[0]["total"]

        internal_notifications = fetch_all(
            """
            SELECT COUNT(*) AS total
            FROM chat_logs
            WHERE notification_type = 'internal_noti'
            """
        )[0]["total"]

        external_notifications = fetch_all(
            """
            SELECT COUNT(*) AS total
            FROM chat_logs
            WHERE notification_type = 'external_noti'
            """
        )[0]["total"]

        return {
            "total_messages": total_messages,
            "network_issues": network_issues,
            "escalations": escalations,
            "internal_notifications": internal_notifications,
            "external_notifications": external_notifications,
        }

    except Exception:
        logger.exception(
            "Unable to calculate dashboard statistics."
        )

        raise HTTPException(
            status_code=500,
            detail="Unable to retrieve statistics.",
        )
