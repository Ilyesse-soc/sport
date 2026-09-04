from io import BytesIO
from uuid import uuid4
from PIL import Image, ImageFile
from fastapi import HTTPException, status

ALLOWED_MIME = {"image/jpeg", "image/png", "image/webp"}
FORMAT_BY_MIME = {
    "image/jpeg": "JPEG",
    "image/png": "PNG",
    "image/webp": "WEBP",
}
EXT_BY_MIME = {
    "image/jpeg": ".jpg",
    "image/png": ".png",
    "image/webp": ".webp",
}

Image.MAX_IMAGE_PIXELS = 16_000_000
ImageFile.LOAD_TRUNCATED_IMAGES = False


def validate_and_reencode_image(data: bytes, mime_type: str, max_bytes: int) -> tuple[bytes, str, str]:
    if mime_type not in ALLOWED_MIME:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Unsupported image type")
    if len(data) > max_bytes:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Image too large")

    try:
        with Image.open(BytesIO(data)) as img:
            img.verify()
        with Image.open(BytesIO(data)) as img:
            img = img.convert("RGB")
            if img.width > 4096 or img.height > 4096:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Image dimensions too large")
            out = BytesIO()
            save_format = FORMAT_BY_MIME[mime_type]
            img.save(out, format=save_format, quality=90, optimize=True)
            clean_bytes = out.getvalue()
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid image file") from exc

    if len(clean_bytes) > max_bytes:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Image too large after processing")

    object_key = f"{uuid4()}{EXT_BY_MIME[mime_type]}"
    return clean_bytes, mime_type, object_key
