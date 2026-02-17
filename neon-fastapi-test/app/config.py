from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()

# Define a Settings class to load environment variables
class Settings(BaseSettings):
    DATABASE_URL: str
    WEBHOOK_SECRET: str

    # Optional: You can add more configuration variables as needed
    class Config:
        env_file = ".env"

settings = Settings()
