import base64
from typing import Optional

import httpx


async def image_to_base64(image_path: str) -> str:
    with open(image_path, "rb") as f:
        return base64.b64encode(f.read()).decode()


async def url_to_base64(url: str) -> str:
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        response.raise_for_status()
        return base64.b64encode(response.content).decode()


def base64_to_file(base64_str: str, output_path: str) -> None:
    data = base64.b64decode(base64_str)
    with open(output_path, "wb") as f:
        f.write(data)


def format_progress_bar(progress: int, width: int = 50) -> str:
    filled = int(width * progress / 100)
    bar = "█" * filled + "░" * (width - filled)
    return f"[{bar}] {progress}%"

