from typing import Any, Dict, Optional

from app.extensions import db
from app.modules.configengine.models import EnvironmentConfig, SystemConfig


class ConfigService:
    """Service for managing system and environment configurations"""

    @staticmethod
    def get_system_config(key: str, default: Any = None) -> Any:
        """Get a system configuration value by key"""
        config = SystemConfig.query.filter_by(key=key).first()
        if config:
            return config.value
        return default

    @staticmethod
    def set_system_config(
        key: str,
        value: Any,
        description: Optional[str] = None,
        category: str = "general",
        is_secret: bool = False,
    ) -> SystemConfig:
        """Set or update a system configuration value"""
        config = SystemConfig.query.filter_by(key=key).first()
        if config:
            config.value = str(value)
            config.description = description or config.description
            config.category = category or config.category
            config.is_secret = is_secret or config.is_secret
        else:
            config = SystemConfig(
                key=key,
                value=str(value),
                description=description,
                category=category,
                is_secret=is_secret,
            )
            db.session.add(config)

        db.session.commit()
        return config

    @staticmethod
    def get_all_system_configs(category: Optional[str] = None) -> list:
        """Get all system configurations, optionally filtered by category"""
        query = SystemConfig.query
        if category:
            query = query.filter_by(category=category)
        return [config.to_dict() for config in query.all()]

    @staticmethod
    def get_environment_config(environment: Optional[str] = None) -> Dict[str, Any]:
        """Get environment configuration"""
        if environment:
            config = EnvironmentConfig.query.filter_by(environment=environment).first()
            return config.to_dict() if config else {}

        # Return merged configuration from all environments
        configs = EnvironmentConfig.query.all()
        merged_config: Dict[str, Any] = {}
        for config_obj in configs:
            merged_config.update(config_obj.app_config or {})
            merged_config["feature_flags"] = {
                **merged_config.get("feature_flags", {}),
                **(config_obj.feature_flags or {}),
            }
        return merged_config

    @staticmethod
    def set_environment_config(
        environment: str, app_config: Dict, feature_flags: Optional[Dict] = None
    ) -> EnvironmentConfig:
        """Set environment configuration"""
        config = EnvironmentConfig.query.filter_by(environment=environment).first()
        if config:
            config.app_config = app_config
            config.feature_flags = feature_flags or config.feature_flags
        else:
            config = EnvironmentConfig(
                environment=environment,
                app_config=app_config,
                feature_flags=feature_flags or {},
            )
            db.session.add(config)

        db.session.commit()
        return config

    @staticmethod
    def get_feature_flag(key: str, default: bool = False) -> bool:
        """Get a feature flag value"""
        config = ConfigService.get_system_config(f"feature_{key}", str(default))
        return config.lower() == "true"

    @staticmethod
    def set_feature_flag(key: str, enabled: bool) -> None:
        """Set a feature flag"""
        ConfigService.set_system_config(
            f"feature_{key}",
            str(enabled),
            description=f"Feature flag: {key}",
            category="feature_flags",
        )


# Initialize service instance
config_service = ConfigService()
