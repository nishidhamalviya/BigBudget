"""Ingredient scanning and detection endpoints (image upload)."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, UploadFile, status

from app.core.config import settings
from app.core.dependencies import get_current_user
from app.schemas.ingredient import DetectResponse, ScanResponse
from app.services.ingredient_service import ingredient_service

router = APIRouter(prefix="/ingredients", tags=["Ingredients"])

_ALLOWED_CONTENT_TYPES = {"image/jpeg", "image/png", "image/webp"}


def _validate_image(file: UploadFile) -> None:
    """Raise 400 if the uploaded file is not an accepted image type or exceeds 10 MB."""

    if file.content_type not in _ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                f"Unsupported file type '{file.content_type}'. "
                f"Accepted types: {', '.join(sorted(_ALLOWED_CONTENT_TYPES))}"
            ),
        )

    if file.size is not None and file.size > settings.MAX_UPLOAD_SIZE_BYTES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File too large. Maximum allowed size is {settings.MAX_UPLOAD_SIZE_BYTES // (1024 * 1024)} MB",
        )


# ── POST /ingredients/scan ───────────────────────────────────────────────────


@router.post(
    "/scan",
    response_model=ScanResponse,
    summary="Scan an image for ingredient text (e.g. food labels)",
)
async def scan_ingredients(
    image: UploadFile,
    current_user: dict = Depends(get_current_user),
) -> ScanResponse:
    """Upload a food label or packaging photo and extract ingredient text using AI vision."""

    _validate_image(image)

    image_bytes = await image.read()

    # Secondary size check for clients that don't send Content-Length
    if len(image_bytes) > settings.MAX_UPLOAD_SIZE_BYTES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File too large. Maximum allowed size is {settings.MAX_UPLOAD_SIZE_BYTES // (1024 * 1024)} MB",
        )

    result = await ingredient_service.scan_image(
        image_bytes=image_bytes,
        user=current_user,
    )
    return result


# ── POST /ingredients/detect ─────────────────────────────────────────────────


@router.post(
    "/detect",
    response_model=DetectResponse,
    summary="Detect food items in a pantry / fridge photo",
)
async def detect_ingredients(
    image: UploadFile,
    current_user: dict = Depends(get_current_user),
) -> DetectResponse:
    """Upload a photo of a fridge or pantry and detect individual food items using AI vision."""

    _validate_image(image)

    image_bytes = await image.read()

    if len(image_bytes) > settings.MAX_UPLOAD_SIZE_BYTES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File too large. Maximum allowed size is {settings.MAX_UPLOAD_SIZE_BYTES // (1024 * 1024)} MB",
        )

    result = await ingredient_service.detect_items(
        image_bytes=image_bytes,
        user=current_user,
    )
    return result
