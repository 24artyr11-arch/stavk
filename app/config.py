import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Settings:
    bot_token: str
    openai_api_key: str
    openai_model: str
    database_path: str
    postback_channel_id: int | None
    admin_ids: set[int]
    admin_username: str
    admin_password: str
    bot_name: str
    daily_analysis_limit: int


def get_settings() -> Settings:
    channel_id = os.getenv("POSTBACK_CHANNEL_ID", "").strip()
    return Settings(
        bot_token=os.getenv("BOT_TOKEN", "").strip(),
        openai_api_key=os.getenv("OPENAI_API_KEY", "").strip(),
        openai_model=os.getenv("OPENAI_MODEL", "gpt-4.1-mini").strip(),
        database_path=os.getenv("DB_PATH", "./data/bot.sqlite3").strip(),
        postback_channel_id=int(channel_id) if channel_id else None,
        admin_ids={int(x) for x in os.getenv("ADMIN_IDS", "").split(",") if x.strip()},
        admin_username=os.getenv("ADMIN_USERNAME", "admin").strip(),
        admin_password=os.getenv("ADMIN_PASSWORD", "").strip(),
        bot_name=os.getenv("BOT_NAME", "AI анализ купонов").strip(),
        daily_analysis_limit=max(1, int(os.getenv("DAILY_ANALYSIS_LIMIT", "3"))),
    )


settings = get_settings()


def validate_settings() -> None:
    missing = [
        name for name, value in (
            ("BOT_TOKEN", settings.bot_token),
            ("OPENAI_API_KEY", settings.openai_api_key),
            ("POSTBACK_CHANNEL_ID", settings.postback_channel_id),
            ("ADMIN_PASSWORD", settings.admin_password),
        ) if not value
    ]
    if missing:
        raise RuntimeError("Заполните обязательные переменные: " + ", ".join(missing))

