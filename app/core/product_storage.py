import os
import base64
import io
from pathlib import Path
from typing import Tuple, Optional, Dict, Any
from PIL import Image
from uuid import uuid4


class ProductStorageError(Exception):
    """Raised when product storage operations fail"""
    pass


def get_products_upload_dir() -> Path:
    """Get the base directory for product uploads"""
    base_dir = Path("app/static/uploads/products")
    base_dir.mkdir(parents=True, exist_ok=True)
    return base_dir


def get_user_products_dir(user_id: str) -> Path:
    """Get the directory for a specific user's product uploads"""
    user_dir = get_products_upload_dir() / user_id
    user_dir.mkdir(parents=True, exist_ok=True)
    return user_dir


def compress_image_if_needed(
    image_data: bytes,
    max_size_bytes: int = 5 * 1024 * 1024,
    quality: int = 85
) -> Tuple[bytes, bool]:
    """
    Compress image if it exceeds the maximum size.

    Args:
        image_data: Original image bytes
        max_size_bytes: Maximum allowed size in bytes (default: 5MB)
        quality: JPEG quality for compression (default: 85)

    Returns:
        Tuple of (compressed_image_bytes, was_compressed)

    Raises:
        ProductStorageError: If image processing fails
    """
    if len(image_data) <= max_size_bytes:
        return image_data, False

    try:
        # Open image
        img = Image.open(io.BytesIO(image_data))

        # Convert to RGB if necessary (for PNG with alpha channel)
        if img.mode in ('RGBA', 'LA', 'P'):
            background = Image.new('RGB', img.size, (255, 255, 255))
            if img.mode == 'P':
                img = img.convert('RGBA')
            background.paste(img, mask=img.split()[-1] if img.mode in ('RGBA', 'LA') else None)
            img = background

        # Compress to JPEG
        output = io.BytesIO()
        img.save(output, format='JPEG', quality=quality, optimize=True)
        compressed_data = output.getvalue()

        # If still too large, reduce quality further
        if len(compressed_data) > max_size_bytes and quality > 50:
            output = io.BytesIO()
            img.save(output, format='JPEG', quality=50, optimize=True)
            compressed_data = output.getvalue()

        return compressed_data, True

    except Exception as e:
        raise ProductStorageError(f"Failed to compress image: {str(e)}")


def prepare_image_for_llm(
    image_data: bytes,
    max_size_bytes: int = 5 * 1024 * 1024,
    quality: int = 85,
) -> Tuple[bytes, Dict[str, Any]]:
    """
    Prepare image bytes for LLM vision models.

    - Converts non-JPEG images to JPEG for compatibility.
    - Compresses images larger than max_size_bytes.

    Returns:
        Tuple of (processed_image_bytes, preprocessing_metadata)
    """
    original_size_bytes = len(image_data)
    original_format = get_image_format(image_data)

    preprocessing: Dict[str, Any] = {
        "original_format": original_format,
        "original_size_bytes": original_size_bytes,
        "processed_format": original_format,
        "processed_size_bytes": original_size_bytes,
        "was_converted": False,
        "was_compressed": False,
        "quality": quality,
        "max_size_bytes": max_size_bytes,
    }

    needs_jpeg = original_format not in {"jpg", "jpeg"}
    needs_compress = original_size_bytes > max_size_bytes

    if not needs_jpeg and not needs_compress:
        return image_data, preprocessing

    try:
        img = Image.open(io.BytesIO(image_data))

        if img.mode in ("RGBA", "LA", "P"):
            background = Image.new("RGB", img.size, (255, 255, 255))
            if img.mode == "P":
                img = img.convert("RGBA")
            background.paste(img, mask=img.split()[-1] if img.mode in ("RGBA", "LA") else None)
            img = background
        elif img.mode != "RGB":
            img = img.convert("RGB")

        output = io.BytesIO()
        img.save(output, format="JPEG", quality=quality, optimize=True)
        processed_data = output.getvalue()

        # If still too large, reduce quality further.
        if len(processed_data) > max_size_bytes and quality > 50:
            output = io.BytesIO()
            img.save(output, format="JPEG", quality=50, optimize=True)
            processed_data = output.getvalue()

        preprocessing["processed_format"] = "jpeg"
        preprocessing["processed_size_bytes"] = len(processed_data)
        preprocessing["was_converted"] = needs_jpeg
        preprocessing["was_compressed"] = needs_compress

        return processed_data, preprocessing

    except Exception as e:
        raise ProductStorageError(f"Failed to prepare image for LLM: {str(e)}")


def save_product_image(
    user_id: str,
    product_id: str,
    image_data: bytes,
    original_format: str = "jpg"
) -> Tuple[str, int]:
    """
    Save a product image to the file system.

    Args:
        user_id: User ID who owns the product
        product_id: Product UUID
        image_data: Image bytes
        original_format: Original file format (jpg, jpeg, png)

    Returns:
        Tuple of (relative_url, file_size_bytes)

    Raises:
        ProductStorageError: If save operation fails
    """
    try:
        # Ensure user directory exists
        user_dir = get_user_products_dir(user_id)

        # Normalize and validate format
        fmt = (original_format or "").lower().lstrip(".")
        if fmt in {"jpg", "jpeg", "png"}:
            ext = fmt
        else:
            raise ProductStorageError(f"Unsupported image format: {original_format}")

        # Generate filename
        filename = f"{product_id}.{ext}"
        file_path = user_dir / filename

        # Save image
        with open(file_path, 'wb') as f:
            f.write(image_data)

        # Generate relative URL
        relative_url = f"/uploads/products/{user_id}/{filename}"

        return relative_url, len(image_data)

    except Exception as e:
        raise ProductStorageError(f"Failed to save product image: {str(e)}")


def delete_product_image(image_url: str) -> bool:
    """
    Delete a product image from the file system.

    Args:
        image_url: Relative image URL (e.g., /uploads/products/{user_id}/{product_id}.jpg)

    Returns:
        True if deleted successfully, False if file doesn't exist

    Raises:
        ProductStorageError: If delete operation fails
    """
    try:
        # Convert URL to file path
        if image_url.startswith('/static/uploads/products/') or image_url.startswith('/uploads/products/'):
            relative_path = image_url
            if image_url.startswith("/static/"):
                relative_path = image_url[len("/static/"):]
            relative_path = relative_path.lstrip("/")
            file_path = Path("app/static") / relative_path

            if file_path.exists():
                file_path.unlink()
                return True
            else:
                return False
        else:
            return False

    except Exception as e:
        raise ProductStorageError(f"Failed to delete product image: {str(e)}")


def image_to_base64(image_data: bytes) -> str:
    """
    Convert image bytes to base64 string.

    Args:
        image_data: Image bytes

    Returns:
        Base64-encoded string
    """
    return base64.b64encode(image_data).decode('utf-8')


def base64_to_image(base64_string: str) -> bytes:
    """
    Convert base64 string to image bytes.

    Args:
        base64_string: Base64-encoded image string

    Returns:
        Image bytes

    Raises:
        ProductStorageError: If decoding fails
    """
    try:
        return base64.b64decode(base64_string)
    except Exception as e:
        raise ProductStorageError(f"Failed to decode base64 image: {str(e)}")


def get_image_format(image_data: bytes) -> str:
    """
    Detect image format from image bytes.

    Args:
        image_data: Image bytes

    Returns:
        Image format (jpg, png, etc.)

    Raises:
        ProductStorageError: If format detection fails
    """
    try:
        img = Image.open(io.BytesIO(image_data))
        return img.format.lower() if img.format else 'jpg'
    except Exception as e:
        raise ProductStorageError(f"Failed to detect image format: {str(e)}")
