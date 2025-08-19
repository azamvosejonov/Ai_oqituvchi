from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List, Optional, Dict, Any, Union
from pydantic import Field, RedisDsn, PostgresDsn, field_validator, HttpUrl, ValidationInfo
from pydantic import EmailStr

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8')

    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Oquv Platformasi"
    BACKEND_CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://127.0.0.1:3000", "http://localhost:8000"]
    ADMIN_IPS: List[str] = ["127.0.0.1"]
    # Database
    DATABASE_URL: str = "sqlite:///home/azam/Desktop/Yaratish/oquv_api_fast/app.db"
    TEST_DATABASE_URL: str = "sqlite:///./test.db"
    # Redis configuration
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_PASSWORD: Optional[str] = None
    REDIS_DB: int = 0
    REDIS_URL: Optional[RedisDsn] = None
    
    # Caching
    USE_CACHE: bool = True
    CACHE_TTL: int = 300  # 5 minutes default
    
    # Monitoring
    ENABLE_MONITORING: bool = True
    METRICS_ENDPOINT: str = "/metrics"
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # Performance
    DATABASE_POOL_SIZE: int = 20
    MAX_OVERFLOW: int = 10
    
    # Security
    RATELIMIT_ENABLED: bool = True
    RATELIMIT_GUEST: str = "100/minute"
    RATELIMIT_USER: str = "500/minute"
    SECRET_KEY: str
    JWT_SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int

    # First Superuser
    FIRST_SUPERUSER: EmailStr
    FIRST_SUPERUSER_PASSWORD: str
    EMAIL_TEST_USER: EmailStr = "test@example.com"
    EMAIL_TEST_USER_PASSWORD: str = "testpassword"

    # Power user for tests/fixtures (fallback to test user if not provided)
    FIRST_POWERUSER: Optional[EmailStr] = None
    FIRST_POWERUSER_PASSWORD: Optional[str] = None

    # Google Gemini
    GOOGLE_AI_API_KEY: Optional[str] = None
    AI_API_KEY: Optional[str] = None

    # Stripe
    STRIPE_API_KEY: Optional[str] = None
    STRIPE_PUBLISHABLE_KEY: Optional[str] = None
    STRIPE_WEBHOOK_SECRET: Optional[str] = None

    # Email
    SMTP_TLS: bool = True
    SMTP_PORT: int = 587
    SMTP_HOST: Optional[str] = None
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    EMAILS_ENABLED: bool = False
    EMAILS_FROM_EMAIL: Optional[EmailStr] = None
    EMAILS_FROM_NAME: Optional[str] = None

    # Debug
    DEBUG: bool = False
    TESTING: bool = False

    # Allowed Origins
    ALLOWED_ORIGINS: Optional[List[str]] = ["*"]
    CORS_ORIGINS: Optional[List[str]] = ["*"]

    # File Uploads
    UPLOAD_DIR: str = "uploads"

    @field_validator("ALLOWED_ORIGINS", "CORS_ORIGINS", mode='before')
    def assemble_origins(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str):
            return [item.strip() for item in v.split(',')]
        return v

    @field_validator("REDIS_URL", mode='before')
    def assemble_redis_connection(cls, v: Optional[str], info: ValidationInfo) -> Any:
        if isinstance(v, str):
            return v
        values = info.data
        # Ensure port is an integer
        port = int(values.get("REDIS_PORT", 6379))
        return str(RedisDsn.build(
            scheme="redis",
            host=values.get("REDIS_HOST", "localhost"),
            port=port,
            path=f"/{values.get('REDIS_DB') or 0}",
            password=values.get("REDIS_PASSWORD") or None,
        ))

    @field_validator("EMAILS_FROM_NAME")
    def get_project_name(cls, v: Optional[str], info: ValidationInfo) -> str:
        if not v:
            return info.data["PROJECT_NAME"]
        return v

    @field_validator("RATELIMIT_GUEST", "RATELIMIT_USER", mode='before')
    def set_rate_limit(cls, v: str, info: ValidationInfo) -> str:
        values = info.data
        if values.get("ENVIRONMENT") == "test":
            return "10000/minute"
        return v

    # Quotas
    FREE_USER_AI_QUOTA: int = 20
    PREMIUM_USER_AI_QUOTA: int = 200
    USER_QUOTA_INTERACTIVE_LESSON: int = 50

    # Free usage window (days) before premium is required on gated features
    FREE_USAGE_DAYS: int = 1

    # API Keys
    GOOGLE_API_KEY: str = ""
    GOOGLE_APPLICATION_CREDENTIALS: Optional[str] = None
    AZURE_SPEECH_KEY: Optional[str] = None
    AZURE_SPEECH_REGION: Optional[str] = None
    XAI_GROK_API_KEY: str = ""
    JWT_ALGORITHM: str = "HS256"
    REFRESH_TOKEN_EXPIRE_DAYS: int = 3  # 3 days

    # reCAPTCHA settings
    RECAPTCHA_SECRET_KEY: Optional[str] = None  # Your Google reCAPTCHA v3 secret key
    RECAPTCHA_SCORE_THRESHOLD: float = 0.5

    # Stripe
    DOMAIN: str = "http://localhost:3000"

    # Alembic
    ALEMBIC_SCRIPT_LOCATION: str = "alembic"

    ENVIRONMENT: str = "development"

    def model_post_init(self, __context: Any) -> None:
        # Provide sensible defaults so tests referencing these attrs don't crash
        if not getattr(self, "FIRST_POWERUSER", None):
            object.__setattr__(self, "FIRST_POWERUSER", self.EMAIL_TEST_USER)
        if not getattr(self, "FIRST_POWERUSER_PASSWORD", None):
            object.__setattr__(self, "FIRST_POWERUSER_PASSWORD", self.EMAIL_TEST_USER_PASSWORD)

settings = Settings()
