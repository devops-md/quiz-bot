"""Application configuration loaded via environment variables."""

from typing import Optional
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configuration settings for DevOps Moldova Quiz Bot."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        populate_by_name=True,
    )

    # Telegram Bot Settings
    bot_token: str = Field(default="", alias="BOT_TOKEN")
    channel_id: str = Field(default="", alias="CHANNEL_ID")
    thread_id: Optional[int] = Field(default=None, alias="THREAD_ID")

    # Scheduling Settings
    publish_time: str = Field(default="08:50", alias="PUBLISH_TIME")
    tz: str = Field(default="Europe/Chisinau", alias="TZ")
    debug_mode: bool = Field(default=False, alias="DEBUG_MODE")
    debug_interval_minutes: int = Field(default=2, alias="DEBUG_INTERVAL_MINUTES")

    # Ollama LLM Settings
    ollama_base_url: str = Field(default="http://ollama:11434", alias="OLLAMA_BASE_URL")
    ollama_model: str = Field(default="llama3.2:3b", alias="OLLAMA_MODEL")
    ollama_timeout: float = Field(default=60.0, alias="OLLAMA_TIMEOUT")
    ollama_temperature: float = Field(default=0.7, alias="OLLAMA_TEMPERATURE")
    ollama_max_retries: int = Field(default=3, alias="OLLAMA_MAX_RETRIES")

    # File Paths
    domains_file_path: str = Field(default="questions_domains.json", alias="DOMAINS_FILE_PATH")
    history_path: str = Field(default="data/history.json", alias="HISTORY_PATH")
    fallback_pool_path: str = Field(default="data/fallback_pool.json", alias="FALLBACK_POOL_PATH")

    @property
    def publish_hour(self) -> int:
        return int(self.publish_time.split(":")[0].strip())

    @property
    def publish_minute(self) -> int:
        return int(self.publish_time.split(":")[1].strip())


settings = Settings()