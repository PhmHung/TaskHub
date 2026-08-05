from fastapi import status

# Standard 401 Unauthorized
UNAUTHORIZED = {
    status.HTTP_401_UNAUTHORIZED: {
        "description": "Authentication required. Invalid or expired token.",
    }
}

# Standard 403 Forbidden
FORBIDDEN = {
    status.HTTP_403_FORBIDDEN: {
        "description": "Not enough permissions to perform this action.",
    }
}

# Combination for most protected endpoints
PROTECTED_RESPONSES = {**UNAUTHORIZED, **FORBIDDEN}

# --- Resource Specific "Not Found" Responses ---

PROJECT_NOT_FOUND = {status.HTTP_404_NOT_FOUND: {"description": "Project not found"}}
WORKSPACE_NOT_FOUND = {status.HTTP_404_NOT_FOUND: {"description": "Workspace not found"}}
TASK_NOT_FOUND = {status.HTTP_404_NOT_FOUND: {"description": "Task not found"}}
LABEL_NOT_FOUND = {status.HTTP_404_NOT_FOUND: {"description": "Label not found"}}
USER_NOT_FOUND = {status.HTTP_404_NOT_FOUND: {"description": "User not found"}}

# --- Conflict Responses ---

CONFLICT = {
    status.HTTP_409_CONFLICT: {
        "description": "A resource with the same identifier already exists."
    }
}
