import os
from typing import Any, Dict, Optional

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _env_bool(key, default=False):
    raw = os.environ.get(key)
    if raw is None:
        return default
    return raw.strip().lower() in ("1", "true", "yes", "on")


def _env_list(key, default=None):
    raw = os.environ.get(key)
    if raw is None:
        return default
    return [item.strip() for item in raw.split(",") if item.strip()]


class Config:
    SECRET_KEY = os.environ.get("FLASK_SECRET_KEY", "dev-secret-key-change-me")
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL", "sqlite:///campaigns.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    CELERY_BROKER_URL = os.environ.get("REDIS_URL", "redis://localhost:6379/0")
    CELERY_RESULT_BACKEND = os.environ.get("REDIS_URL", "redis://localhost:6379/0")
    UPLOAD_FOLDER = os.environ.get("UPLOAD_FOLDER", os.path.join(BASE_DIR, "uploads"))
    MAX_FILE_SIZE = int(os.environ.get("MAX_FILE_SIZE", 52428800))
    MAX_CONTENT_LENGTH = int(os.environ.get("MAX_FILE_SIZE", 52428800))
    ALLOWED_AUDIO_EXTENSIONS = {
        "wav",
        "mp3",
        "gsm",
        "ogg",
        "flac",
        "m4a",
        "mp4",
        "aiff",
    }
    ALLOWED_NUMBER_EXTENSIONS = {"txt", "csv", "xlsx", "xls"}
    ALLOWED_TEMPLATE_EXTENSIONS = {"txt", "html", "json", "md"}
    ALLOWED_IMAGE_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp", "svg"}
    ALLOWED_DOCUMENT_EXTENSIONS = {"pdf", "doc", "docx", "xls", "xlsx", "ppt", "pptx"}
    LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO")
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    PERMANENT_SESSION_LIFETIME = 3600
    ENV_NAME = "base"
    SESSION_COOKIE_SECURE = False
    WTF_CSRF_ENABLED = True
    AUTO_CREATE_TABLES = True

    @staticmethod
    def init_app(app):
        return None


class DevelopmentConfig(Config):
    ENV_NAME = "development"
    DEBUG = True
    SQLALCHEMY_ECHO = False
    SESSION_COOKIE_SECURE = False


class TestingConfig(Config):
    ENV_NAME = "testing"
    TESTING = True
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.environ.get("TEST_DATABASE_URL", "sqlite:///:memory:")
    WTF_CSRF_ENABLED = False
    SESSION_COOKIE_SECURE = False
    CELERY_TASK_ALWAYS_EAGER = True


class BetaConfig(Config):
    ENV_NAME = "beta"
    DEBUG = False
    TESTING = False
    SESSION_COOKIE_SECURE = True
    AUTO_CREATE_TABLES = False


class StagingConfig(Config):
    ENV_NAME = "staging"
    DEBUG = False
    TESTING = False
    SESSION_COOKIE_SECURE = True
    AUTO_CREATE_TABLES = False


class ProductionConfig(Config):
    ENV_NAME = "production"
    DEBUG = False
    TESTING = False
    SESSION_COOKIE_SECURE = True
    AUTO_CREATE_TABLES = False
    SQLALCHEMY_ECHO = False
    PREFERRED_URL_SCHEME = "https"

    @staticmethod
    def init_app(app):
        insecure = app.config.get("SECRET_KEY") in (
            None,
            "",
            "dev-secret-key-change-me",
        )
        if insecure and not _env_bool("ALLOW_INSECURE_SECRET_KEY"):
            raise RuntimeError(
                "FLASK_SECRET_KEY must be set to a strong unique value in production. "
                "Set ALLOW_INSECURE_SECRET_KEY=true only to override deliberately."
            )
        if app.config.get("SQLALCHEMY_DATABASE_URI", "").startswith("sqlite"):
            app.logger.warning(
                "Production is running on SQLite. Migrate to PostgreSQL/Cloud SQL "
                "before scaling (Module 00, Stage 3)."
            )


config = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "beta": BetaConfig,
    "staging": StagingConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig,
}


class ConfigLoader:
    @staticmethod
    def load_config(env_name: Optional[str] = None) -> Config:
        if env_name is None:
            env_name = os.environ.get("FLASK_ENV", "development")

        config_class = config.get(env_name, config["default"])
        return config_class()

    @staticmethod
    def validate_config(config_obj: Config) -> Dict[str, Any]:
        warnings = []
        errors = []

        if config_obj.ENV_NAME != "development":
            if "dev-secret-key" in config_obj.SECRET_KEY:
                warnings.append(
                    "Using development SECRET_KEY in non-development environment"
                )

        if not config_obj.SQLALCHEMY_DATABASE_URI:
            errors.append("SQLALCHEMY_DATABASE_URI is not set")

        if config_obj.MAX_CONTENT_LENGTH > 100 * 1024 * 1024:
            warnings.append("MAX_CONTENT_LENGTH is very large (>100MB)")

        return {"warnings": warnings, "errors": errors, "is_valid": len(errors) == 0}
