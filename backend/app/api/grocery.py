"""Grocery list generation and export endpoints."""

from __future__ import annotations

from io import BytesIO

from fastapi import APIRouter, Depends, status
from fastapi.responses import StreamingResponse
from prisma import Prisma

from app.core.dependencies import get_current_user, get_db
from app.schemas.grocery import GroceryGenerateRequest, GroceryListResponse
from app.services.grocery_service import grocery_service

router = APIRouter(prefix="/grocery", tags=["Grocery"])


# ── POST /grocery/generate ───────────────────────────────────────────────────


@router.post(
    "/generate",
    response_model=GroceryListResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Generate a grocery list from meal plans",
)
async def generate_grocery_list(
    body: GroceryGenerateRequest,
    current_user: dict = Depends(get_current_user),
    db: Prisma = Depends(get_db),
) -> GroceryListResponse:
    """Aggregate ingredients from the specified meal plans (or recent history)
    into a de-duplicated, budget-optimised grocery list.
    """

    result = await grocery_service.generate_list(
        user=current_user,
        request=body,
        db=db,
    )
    return result


# ── GET /grocery/export/pdf ──────────────────────────────────────────────────


@router.get(
    "/export/pdf",
    summary="Export the latest grocery list as PDF",
    responses={
        200: {
            "content": {"application/pdf": {}},
            "description": "PDF file download",
        }
    },
)
async def export_pdf(
    current_user: dict = Depends(get_current_user),
    db: Prisma = Depends(get_db),
) -> StreamingResponse:
    """Generate and stream a PDF document containing the user's most recent
    grocery list.
    """

    pdf_bytes: bytes = await grocery_service.export_pdf(
        user=current_user,
        db=db,
    )

    return StreamingResponse(
        BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers={
            "Content-Disposition": "attachment; filename=grocery_list.pdf",
        },
    )


# ── GET /grocery/export/csv ──────────────────────────────────────────────────


@router.get(
    "/export/csv",
    summary="Export the latest grocery list as CSV",
    responses={
        200: {
            "content": {"text/csv": {}},
            "description": "CSV file download",
        }
    },
)
async def export_csv(
    current_user: dict = Depends(get_current_user),
    db: Prisma = Depends(get_db),
) -> StreamingResponse:
    """Generate and stream a CSV document containing the user's most recent
    grocery list.
    """

    csv_bytes: bytes = await grocery_service.export_csv(
        user=current_user,
        db=db,
    )

    return StreamingResponse(
        BytesIO(csv_bytes),
        media_type="text/csv",
        headers={
            "Content-Disposition": "attachment; filename=grocery_list.csv",
        },
    )
