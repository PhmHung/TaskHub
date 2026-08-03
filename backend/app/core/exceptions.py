from fastapi import HTTPException, status


def http_401_exc(detail: str = "Could not validate credentials"):
    """
    Returns an HTTPException with status code 401 Unauthorized.
    """
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=detail,
        headers={"WWW-Authenticate": "Bearer"},
    )

def http_403_exc(detail: str = "Not authorized to perform this action."):
    """
    Returns an HTTPException with status code 403 Forbidden.
    """
    return HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail=detail,
    )


def http_404_exc(detail: str = "Resource not found."):
    """
    Returns an HTTPException with status code 404 Not Found.
    """
    return HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=detail,
    )


def http_400_exc(detail: str = "Bad request."):
    """
    Returns an HTTPException with status code 400 Bad Request.
    """
    return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)

def http_409_exc(detail: str = "Conflict"):
    return HTTPException(status_code=status.HTTP_409_CONFLICT, detail=detail)

class ConfigurationError(Exception):
    """Custom exception for application configuration errors."""

    def __init__(self, message: str = "Application configuration error."):
        self.message = message
        super().__init__(self.message)
