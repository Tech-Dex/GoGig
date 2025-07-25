import os

from dotenv import load_dotenv

load_dotenv()


class Settings:
    # Discord Configuration
    DISCORD_TOKEN: str = os.getenv("DISCORD_TOKEN")
    DISCORD_GUILD_ID: int = int(os.getenv("DISCORD_GUILD_ID", 0))
    DISCORD_CHANNEL_ID: int = int(os.getenv("DISCORD_CHANNEL_ID", 0))
    DISCORD_LOGS_CHANNEL_ID: int = int(os.getenv("DISCORD_LOGS_CHANNEL_ID", 0))

    # Reddit Configuration
    REDDIT_CLIENT_ID: str = os.getenv("REDDIT_CLIENT_ID")
    REDDIT_CLIENT_SECRET: str = os.getenv("REDDIT_CLIENT_SECRET")
    REDDIT_USER_NAME: str = os.getenv("REDDIT_USER_NAME")
    REDDIT_PASSWORD: str = os.getenv("REDDIT_PASSWORD")
    REDDIT_USER_AGENT: str = os.getenv("REDDIT_USER_AGENT")

    # PostgreSQL Configuration
    POSTGRES_HOST: str = os.getenv("POSTGRES_HOST", "localhost")
    POSTGRES_PORT: int = int(os.getenv("POSTGRES_PORT", 5432))
    POSTGRES_USER: str = os.getenv("POSTGRES_USER")
    POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD")
    POSTGRES_DATABASE: str = os.getenv("POSTGRES_DATABASE")

    # Application Settings
    CHECK_INTERVAL: int = int(os.getenv("CHECK_INTERVAL", 10))
    MAX_JOBS_PER_CHECK: int = int(os.getenv("MAX_JOBS_PER_CHECK", 10))


settings = Settings()
