# This file defines what settings our application needs but the actual values
# come from our .env file which is top CIA secret
# ------- IMPORTS -------
from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

# ------- CLASSES -------
class Settings(BaseSettings):
    # Congifures Pydantic to look for a .env file.
    # The .env file is for storing sensitive info like keys.
    model_config = SettingsConfigDict(
        env_file = ".env",
        env_file_encoding = "utf-8",
    )

    # The secret key found in the .env.
    secret_key: SecretStr
    # Standard defaults for JWT.
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

# ------- SETUP -------
# Loaded from the .env
settings = Settings()