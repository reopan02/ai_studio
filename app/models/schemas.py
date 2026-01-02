from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, EmailStr, Field
from pydantic.config import ConfigDict


class TaskStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class ModelType(str, Enum):
    SORA2 = "sora2"
    VEO = "veo"
    SEEDANCE = "seedance"
    NEWMODEL = "newmodel"


class VideoGenerationRequest(BaseModel):
    model: ModelType
    prompt: str
    image: Optional[str] = None
    duration: Optional[int] = Field(default=10, ge=1, le=25)
    aspect_ratio: Optional[str] = "16:9"
    resolution: Optional[str] = "1080p"
    extra_params: Optional[Dict[str, Any]] = None


class TaskResponse(BaseModel):
    model_config = ConfigDict(validate_assignment=True)

    task_id: str
    status: TaskStatus
    progress: int = 0
    message: Optional[str] = None
    video_url: Optional[str] = None
    video_base64: Optional[str] = None
    error: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class ProgressCallback(BaseModel):
    task_id: str
    progress: int
    status: TaskStatus
    message: str


class UserRegisterRequest(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(min_length=6, max_length=128)


class UserLoginRequest(BaseModel):
    username_or_email: str = Field(min_length=3, max_length=255)
    password: str = Field(min_length=6, max_length=128)


class UserPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    username: str
    email: EmailStr
    is_active: bool
    is_admin: bool
    created_at: datetime
    last_login_at: Optional[datetime] = None


class AdminLoginAttempt(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    user_id: Optional[str] = None
    username_or_email: str
    success: bool
    failure_reason: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    created_at: datetime


class AdminUserSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    username: str
    email: EmailStr
    is_active: bool
    is_admin: bool
    storage_quota_bytes: int
    storage_used_bytes: int
    created_at: datetime
    last_login_at: Optional[datetime] = None


class AdminUserDetail(AdminUserSummary):
    total_video_count: int
    total_image_count: int
    active_session_count: int
    recent_login_attempts: List[AdminLoginAttempt]


class AdminUserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    is_active: Optional[bool] = None
    is_admin: Optional[bool] = None
    storage_quota_bytes: Optional[int] = Field(default=None, ge=0)


class AdminSystemStats(BaseModel):
    total_user_count: int
    active_user_count: int
    total_storage_used_bytes: int
    total_storage_quota_bytes: int
    total_video_count: int
    total_image_count: int
    active_session_count: int


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    session_id: str


class RequestCategoryCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    description: Optional[str] = Field(default=None, max_length=1000)


class RequestCategoryUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=100)
    description: Optional[str] = Field(default=None, max_length=1000)


class RequestCategoryOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    description: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None


class ApiRequestLogSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    user_id: Optional[str] = None
    category_id: Optional[str] = None
    method: str
    path: str
    response_status_code: int
    duration_ms: int
    started_at: datetime


class ApiRequestLogDetail(ApiRequestLogSummary):
    query_params: Optional[Dict[str, Any]] = None
    request_headers: Optional[Dict[str, Any]] = None
    request_body_json: Optional[Any] = None
    request_body_text: Optional[str] = None

    response_headers: Optional[Dict[str, Any]] = None
    response_body_json: Optional[Any] = None
    response_body_text: Optional[str] = None

    tags: Optional[List[str]] = None
    note: Optional[str] = None
    error_message: Optional[str] = None

    client_ip: Optional[str] = None
    user_agent: Optional[str] = None
    finished_at: datetime


class ApiRequestLogUpdate(BaseModel):
    category_id: Optional[str] = None
    tags: Optional[List[str]] = None
    note: Optional[str] = Field(default=None, max_length=5000)


class UserVideoCreate(BaseModel):
    title: Optional[str] = Field(default=None, max_length=200)
    model: str = Field(min_length=1, max_length=50)
    prompt: str = Field(min_length=1)
    video_url: str = Field(min_length=1, max_length=500)
    status: str = Field(default="completed", min_length=1, max_length=20)
    # Optional fields for detailed storage if available
    metadata: Optional[Dict[str, Any]] = None


class UserVideoGenerateRequest(BaseModel):
    title: Optional[str] = Field(default=None, max_length=200)
    generation: VideoGenerationRequest


class UserVideoUpdate(BaseModel):
    title: Optional[str] = Field(default=None, max_length=200)


class UserVideoSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    title: Optional[str] = None
    model: str
    prompt: str
    status: str
    video_url: Optional[str] = None
    size_bytes: int
    created_at: datetime
    updated_at: Optional[datetime] = None


class UserVideoDetail(UserVideoSummary):
    request: Dict[str, Any]
    response: Dict[str, Any]


class UserImageCreate(BaseModel):
    title: Optional[str] = Field(default=None, max_length=200)
    model: str = Field(min_length=1, max_length=100)
    prompt: str = Field(min_length=1)
    image_url: Optional[str] = Field(default=None, max_length=1000)
    status: str = Field(default="completed", min_length=1, max_length=20)
    metadata: Optional[Dict[str, Any]] = None
    request: Optional[Dict[str, Any]] = None
    response: Optional[Dict[str, Any]] = None


class UserImageUpdate(BaseModel):
    title: Optional[str] = Field(default=None, max_length=200)


class UserImageSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    title: Optional[str] = None
    model: str
    prompt: str
    status: str
    image_url: Optional[str] = None
    size_bytes: int
    created_at: datetime
    updated_at: Optional[datetime] = None


class UserImageDetail(UserImageSummary):
    request: Dict[str, Any]
    response: Dict[str, Any]


class StorageUsage(BaseModel):
    quota_bytes: int
    used_bytes: int


class UserQuotaUpdate(BaseModel):
    storage_quota_bytes: int = Field(ge=0)


class ProductRecognitionResult(BaseModel):
    name: str
    dimensions: Optional[str] = None
    features: List[str] = []
    characteristics: List[str] = []
    confidence: float = Field(ge=0.0, le=1.0)


class ProductRecognitionResponse(BaseModel):
    """Response from preview recognition endpoint"""
    name: str
    dimensions: Optional[str] = None
    features: List[str] = []
    characteristics: List[str] = []
    confidence: float = Field(ge=0.0, le=1.0)
    metadata: Optional[Dict[str, Any]] = None


class ProductCreate(BaseModel):
    name: Optional[str] = Field(default=None, max_length=200)
    dimensions: Optional[str] = Field(default=None, max_length=100)
    features: Optional[List[str]] = None
    characteristics: Optional[List[str]] = None


class ProductUpdate(BaseModel):
    name: Optional[str] = Field(default=None, max_length=200)
    dimensions: Optional[str] = Field(default=None, max_length=100)
    features: Optional[List[str]] = None
    characteristics: Optional[List[str]] = None


class ProductSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    user_id: str
    id: str
    name: str
    dimensions: Optional[str] = None
    original_image_url: str
    recognition_confidence: Optional[float] = None
    image_size_bytes: int
    image_count: int = 1
    created_at: datetime
    updated_at: Optional[datetime] = None


class ProductImageSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    image_url: str
    image_size_bytes: int
    is_primary: bool
    created_at: datetime
    updated_at: Optional[datetime] = None


class ProductDetail(ProductSummary):
    features: Optional[List[str]] = None
    characteristics: Optional[List[str]] = None
    recognition_metadata: Optional[Dict[str, Any]] = None
    images: List[ProductImageSummary] = Field(default_factory=list)


class ProductListResponse(BaseModel):
    products: List[ProductSummary]
    total: int
    offset: int
    limit: int

