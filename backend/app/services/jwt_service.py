from typing import Any, Dict, Optional

from jose import JWTError, jwt

from app.core.config import settings

def _decode_token(token: str, expected_type: Optional[str] = None) -> Optional[Dict[str, Any]]:
    try:
        payload = jwt.decode(
            token, settings.secret_key, algorithms=[settings.algorithm]
        )
        if expected_type and payload.get("type") != expected_type:
            return None
        return payload
    except JWTError:
        return None


def decode_access_token(token: str) -> Optional[Dict[str, Any]]:
    return _decode_token(token, expected_type="access")


def decode_refresh_token(token: str) -> Optional[Dict[str, Any]]:
    return _decode_token(token, expected_type="refresh")