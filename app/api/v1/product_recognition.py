from __future__ import annotations

from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status

from app.api.deps import AuthContext, get_current_user
from app.clients.llm_client import ProductRecognitionError, recognize_product_with_metadata
from app.core.product_storage import (
    ProductStorageError,
    get_image_format,
    image_to_base64,
    prepare_image_for_llm,
)
from app.models.schemas import ProductRecognitionResponse

router = APIRouter()


@router.post("/products/recognize", response_model=ProductRecognitionResponse)
async def recognize_product_preview(
    image: UploadFile = File(...),
    raw_text: Optional[str] = Form(None),
    _auth: AuthContext = Depends(get_current_user),
):
    """
    Preview recognition: extract product attributes from image + optional raw text.

    This endpoint performs AI recognition but does NOT persist anything.
    """
    image_data = await image.read()
    if len(image_data) == 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Empty image file")

    try:
        detected_format = get_image_format(image_data)
    except ProductStorageError:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Invalid or unsupported image file")

    if detected_format not in {"jpeg", "png"}:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Only JPEG and PNG images are supported")

    llm_image_data, preprocessing = prepare_image_for_llm(image_data)
    llm_mime_type = "image/jpeg" if preprocessing["processed_format"] in {"jpg", "jpeg"} else "image/png"

    try:
        image_base64 = image_to_base64(llm_image_data)

        recognition_result, llm_metadata = await recognize_product_with_metadata(
            image_base64,
            mime_type=llm_mime_type,
            raw_text=raw_text,
        )

        recognition_metadata = {
            "recognized_at": datetime.utcnow().isoformat(),
            "model": "structllm",
            "confidence": recognition_result.confidence,
            "preprocessing": preprocessing,
            "llm": llm_metadata,
        }

        return ProductRecognitionResponse(
            name=recognition_result.name,
            dimensions=recognition_result.dimensions,
            features=recognition_result.features,
            characteristics=recognition_result.characteristics,
            confidence=recognition_result.confidence,
            metadata=recognition_metadata,
        )
    except (ProductRecognitionError, Exception) as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Product recognition failed: {exc}",
        )

