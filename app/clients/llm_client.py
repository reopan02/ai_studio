import os
from typing import Optional, Any, Dict, Tuple
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from tenacity import retry, stop_after_attempt, wait_exponential

try:
    from structllm import StructLLM
    STRUCTLLM_AVAILABLE = True
except ImportError:
    STRUCTLLM_AVAILABLE = False

from app.models.schemas import ProductRecognitionResult

load_dotenv()


class LLMConfig:
    """Configuration for LLM API"""
    api_key: str = os.getenv("API_KEY", "")
    base_url: str = os.getenv("API_BASE_URL", "https://api.gpt-best.com")
    model: str = os.getenv("LLM_MODEL", "openai/gpt-4o-mini")

    @classmethod
    def get_base_url(cls) -> str:
        """Get base URL with /v1 suffix if needed"""
        if cls.base_url and not cls.base_url.endswith("/v1"):
            return f"{cls.base_url}/v1"
        return cls.base_url


class ProductRecognitionError(Exception):
    """Raised when product recognition fails"""
    pass


_PLACEHOLDER_API_KEYS = {
    "your-provider-api-key",
    "your_api_key_here",
    "your-api-key",
    "your-provider-key",
    "changeme",
    "replace-me",
}


def _safe_dump_raw_response(raw_response: Any) -> Dict[str, Any]:
    try:
        if hasattr(raw_response, "model_dump"):
            return raw_response.model_dump()  # type: ignore[no-any-return]
        if hasattr(raw_response, "dict"):
            return raw_response.dict()  # type: ignore[no-any-return]
    except Exception:
        pass
    return {"raw_response": str(raw_response)}


def create_llm_client() -> Optional[object]:
    """Create StructLLM client instance"""
    if not STRUCTLLM_AVAILABLE:
        return None

    config = LLMConfig()
    api_key = (config.api_key or "").strip()
    if not api_key or api_key in _PLACEHOLDER_API_KEYS:
        return None

    try:
        client = StructLLM(
            api_key=api_key,
            api_base=config.get_base_url()
        )
        return client
    except Exception as e:
        print(f"Failed to initialize StructLLM client: {e}")
        return None


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=10),
    reraise=True
)
async def recognize_product_with_metadata(
    image_base64: str,
    mime_type: str = "image/jpeg",
) -> Tuple[ProductRecognitionResult, Dict[str, Any]]:
    """
    Recognize product attributes from an image using LLM vision capabilities.

    Args:
        image_base64: Base64-encoded product image
        mime_type: MIME type for the image data URI

    Returns:
        Tuple of (ProductRecognitionResult, metadata)

    Raises:
        ProductRecognitionError: If recognition fails after retries
    """
    if not STRUCTLLM_AVAILABLE:
        raise ProductRecognitionError("StructLLM library is not installed. Install with: pip install structllm")

    client = create_llm_client()
    if not client:
        raise ProductRecognitionError("Failed to initialize LLM client. Check API_KEY and API_BASE_URL configuration.")

    # System prompt for product recognition
    system_prompt = """你是一个专业的产品识别助手。请仔细观察图片中的产品,并提取以下信息:
- 产品名称(name): 简洁准确的产品名称
- 尺寸规格(dimensions): 产品的尺寸、容量等规格信息
- 功能特征(features): 产品的主要功能特点,以列表形式返回
- 产品特点(characteristics): 产品的特色标签,如"便携"、"大容量"等,以列表形式返回
- 置信度(confidence): 你对识别结果的置信度,0.0-1.0之间的浮点数

如果图片不清晰或信息不足,请将置信度设置为较低值。"""

    # User prompt with structured output request
    user_prompt = """识别这张图片中的产品,返回产品名称、尺寸、功能特征和特点。
请确保返回的JSON格式包含以下字段:
- name: 产品名称(字符串)
- dimensions: 尺寸规格(字符串,如果无法识别则为null)
- features: 功能特征列表(字符串数组)
- characteristics: 产品特点列表(字符串数组)
- confidence: 置信度(0.0-1.0之间的浮点数)"""

    try:
        # Call LLM API with structured output
        response = client.parse(
            model=LLMConfig.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": user_prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:{mime_type};base64,{image_base64}"
                            }
                        }
                    ]
                }
            ],
            response_format=ProductRecognitionResult
        )

        result = response.output_parsed

        if not result:
            raise ProductRecognitionError("LLM returned empty result")

        # Ensure confidence is within valid range
        if result.confidence < 0.0:
            result.confidence = 0.0
        elif result.confidence > 1.0:
            result.confidence = 1.0

        metadata: Dict[str, Any] = {"raw_response": _safe_dump_raw_response(response.raw_response)}
        try:
            metadata["raw_content"] = response.raw_response.choices[0].message.content
        except Exception:
            pass

        return result, metadata

    except Exception as e:
        raise ProductRecognitionError(f"Product recognition failed: {str(e)}")


async def recognize_product(image_base64: str) -> ProductRecognitionResult:
    result, _ = await recognize_product_with_metadata(image_base64)
    return result


def create_manual_recognition_result(
    name: str = "未命名产品",
    dimensions: Optional[str] = None,
    features: Optional[list] = None,
    characteristics: Optional[list] = None
) -> ProductRecognitionResult:
    """
    Create a manual recognition result for products entered without AI recognition.

    Args:
        name: Product name
        dimensions: Product dimensions
        features: Product features list
        characteristics: Product characteristics list

    Returns:
        ProductRecognitionResult with confidence=0.0 indicating manual entry
    """
    return ProductRecognitionResult(
        name=name,
        dimensions=dimensions,
        features=features or [],
        characteristics=characteristics or [],
        confidence=0.0
    )
