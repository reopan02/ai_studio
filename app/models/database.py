import enum
from uuid import uuid4

from sqlalchemy import (
    JSON,
    Boolean,
    CheckConstraint,
    Column,
    DateTime,
    Enum as SQLEnum,
    ForeignKey,
    Integer,
    LargeBinary,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()


class TaskStatusDB(enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class VideoTask(Base):
    __tablename__ = "video_tasks"

    id = Column(String(36), primary_key=True)
    model = Column(String(50), nullable=False)
    prompt = Column(Text, nullable=False)
    status = Column(SQLEnum(TaskStatusDB), default=TaskStatusDB.PENDING)
    progress = Column(Integer, default=0)

    input_image_base64 = Column(Text, nullable=True)
    params = Column(Text, nullable=True)

    video_url = Column(String(500), nullable=True)
    video_base64 = Column(Text, nullable=True)

    error_message = Column(Text, nullable=True)
    retry_count = Column(Integer, default=0)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)


class User(Base):
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    username = Column(String(50), nullable=False, unique=True, index=True)
    email = Column(String(255), nullable=False, unique=True, index=True)
    password_hash = Column(String(255), nullable=False)

    is_active = Column(Boolean, nullable=False, default=True)
    is_admin = Column(Boolean, nullable=False, default=False)

    storage_quota_bytes = Column(Integer, nullable=False, default=1_073_741_824)
    storage_used_bytes = Column(Integer, nullable=False, default=0)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_login_at = Column(DateTime(timezone=True), nullable=True)


class UserSession(Base):
    __tablename__ = "user_sessions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False, index=True)
    revoked_at = Column(DateTime(timezone=True), nullable=True)

    ip_address = Column(String(45), nullable=True)
    user_agent = Column(String(300), nullable=True)


class UserLoginLog(Base):
    __tablename__ = "user_login_logs"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    user_id = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    username_or_email = Column(String(255), nullable=False)
    success = Column(Boolean, nullable=False)
    failure_reason = Column(Text, nullable=True)

    ip_address = Column(String(45), nullable=True)
    user_agent = Column(String(300), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)


class UserVideo(Base):
    __tablename__ = "user_videos"
    __table_args__ = (
        CheckConstraint("size_bytes >= 0", name="ck_user_videos_size_bytes"),
    )

    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)

    title = Column(String(200), nullable=True, index=True)
    model = Column(String(50), nullable=False, index=True)
    prompt = Column(Text, nullable=False)

    status = Column(String(20), nullable=False, default="completed", index=True)
    video_url = Column(String(500), nullable=True)

    request_encrypted = Column(LargeBinary, nullable=False)
    response_encrypted = Column(LargeBinary, nullable=False)
    size_bytes = Column(Integer, nullable=False, default=0)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class UserImage(Base):
    __tablename__ = "user_images"
    __table_args__ = (
        CheckConstraint("size_bytes >= 0", name="ck_user_images_size_bytes"),
    )

    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)

    title = Column(String(200), nullable=True, index=True)
    model = Column(String(100), nullable=False, index=True)
    prompt = Column(Text, nullable=False)

    status = Column(String(20), nullable=False, default="completed", index=True)
    image_url = Column(String(1000), nullable=True)

    request_encrypted = Column(LargeBinary, nullable=False)
    response_encrypted = Column(LargeBinary, nullable=False)
    size_bytes = Column(Integer, nullable=False, default=0)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class RequestCategory(Base):
    __tablename__ = "request_categories"
    __table_args__ = (
        UniqueConstraint("owner_user_id", "name", name="uq_request_categories_owner_name"),
    )

    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    owner_user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)

    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class ApiRequestLog(Base):
    __tablename__ = "api_request_logs"
    __table_args__ = (
        CheckConstraint("duration_ms >= 0", name="ck_api_request_logs_duration_ms"),
        CheckConstraint(
            "response_status_code >= 100 AND response_status_code <= 599",
            name="ck_api_request_logs_status_code",
        ),
    )

    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    user_id = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    session_id = Column(
        String(36),
        ForeignKey("user_sessions.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    category_id = Column(
        String(36),
        ForeignKey("request_categories.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    method = Column(String(10), nullable=False)
    path = Column(String(500), nullable=False, index=True)
    query_params = Column(JSON, nullable=True)
    request_headers = Column(JSON, nullable=True)
    request_body_json = Column(JSON, nullable=True)
    request_body_text = Column(Text, nullable=True)

    response_status_code = Column(Integer, nullable=False, index=True)
    response_headers = Column(JSON, nullable=True)
    response_body_json = Column(JSON, nullable=True)
    response_body_text = Column(Text, nullable=True)

    tags = Column(JSON, nullable=True)
    note = Column(Text, nullable=True)

    error_message = Column(Text, nullable=True)

    client_ip = Column(String(45), nullable=True)
    user_agent = Column(String(300), nullable=True)

    started_at = Column(DateTime(timezone=True), nullable=False, index=True)
    finished_at = Column(DateTime(timezone=True), nullable=False)
    duration_ms = Column(Integer, nullable=False)
