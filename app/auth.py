# ------- IMPORTS -------
from datetime import UTC, datetime, timedelta

import jwt
from fastapi.security import OAuth2PasswordBearer
from pwdlib import PasswordHash

from config import settings

# ------- SETUP -------
# Creates a password hasher using Argon2 recommended defaults.
password_hash = PasswordHash.recommended()

# Tells FastAPI where the token login endpoint lives. Used for Swagger docs.
oauth2_scheme = OAuth2PasswordBearer(tokenUrl = "api/users/token")

# ------- HELPERS -------
# Takes a plain password and scrambles (hashes) it.
def hash_password(password: str) -> str:
    return password_hash.hash(password)

# Compare a plain password against the hashed one.
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return password_hash.verify(plain_password, hashed_password)

# ------- LOGIC -------
def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()

    # Calculate the future timestamp when the token expires
    if expires_delta:
        expire = datetime.now(UTC) + expires_delta
    else:
        # Uses the default fallback defined in config (30 minutes)
        expire = datetime.now(UTC) + timedelta(minutes = settings.access_token_expire_minutes,)

    # Adds the expiration time to the payload.
    to_encode.update({"exp": expire})

    # (Avengers) Assemble the final JWT token with the payload, header and signiture
    encoded_jwt = jwt.encode(
        to_encode,
        # The key is securely taken from the .env.
        settings.secret_key.get_secret_value(),
        algorithm = settings.algorithm,
    )

    return encoded_jwt

# Check to see if the access token is valid.
def verify_access_token(token: str) -> str | None:
    try:
        # Decrypts and verifies the token.
        payload = jwt.decode(
            token,
            settings.secret_key.get_secret_value(),
            algorithms = [settings.algorithm],
            # Check that the token hasn't expired and it contains a subject user ID.
            options = {"require": ["exp", "sub"]},
        )
    except jwt.InvalidTokenError:
        return None
    else:
        # Returns the user ID if valid
        return payload.get("sub")