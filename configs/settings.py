"""
全局配置管理
使用 pydantic-settings 实现类型安全的配置管理
"""
import os
import json
from pathlib import Path
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """全局配置类"""

    # 环境配置
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )

    # 当前环境
    environment: str = "dev"

    # 基础URL
    base_url: str = "https://testerp.xjcec.com"
    api_url: str = "https://testerp.xjcec.com/api"

    # 超时配置 (毫秒)
    timeout: int = 30000
    navigation_timeout: int = 60000

    # 浏览器配置
    headless: bool = True
    slow_mo: int = 100  # 慢动作模式（毫秒），方便调试
    browser: str = "chromium"  # chromium, firefox, webkit

    # 截图配置
    screenshot_on_fail: bool = True
    screenshot_dir: str = "screenshots"

    # Trace配置
    trace_on_fail: bool = True
    trace_dir: str = "traces"

    # 并行配置
    workers: int = 1  # pytest-xdist worker数量

    # 重试配置
    max_retries: int = 2

    # 测试账号
    admin_username: str = "13260630892"
    admin_password: str = "Aa123456"

    def load_env_config(self):
        """从JSON文件加载环境配置"""
        config_dir = Path(__file__).parent.parent / "configs"
        config_file = config_dir / f"{self.environment}.json"

        if config_file.exists():
            with open(config_file, "r", encoding="utf-8") as f:
                config = json.load(f)
                for key, value in config.items():
                    if hasattr(self, key):
                        setattr(self, key, value)

    @property
    def is_dev(self) -> bool:
        return self.environment == "dev"

    @property
    def is_staging(self) -> bool:
        return self.environment == "staging"

    @property
    def is_production(self) -> bool:
        return self.environment == "production"


# 全局配置实例
settings = Settings()
settings.load_env_config()
