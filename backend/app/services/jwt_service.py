from typing import Any, Dict, Optional

from jose import JWTError, jwt

from app.core.config import settings


def decode_access_token(token: str) -> Optional[Dict[str, Any]]:

    try:
        payload = jwt.decode(
            token, settings.secret_key, algorithms=[settings.algorithm]
        )
        return payload
    except JWTError:
        return None


def decode_refresh_token(token: str) -> Optional[Dict[str, Any]]:

    try:
        payload = jwt.decode(
            token, settings.secret_key, algorithms=[settings.algorithm]
        )
        return payload
    except JWTError:
        return None