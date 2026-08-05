from fastapi import Query

from app.enums import TaskPriority, TaskStatus


async def get_pagination_params(
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(20, ge=1, le=100, description="Page size"),
) -> dict[str, int]:
    return {"page": page, "size": size}


async def get_task_filter_params(
    status: TaskStatus | None = Query(None, description="Filter by task status"),
    priority: TaskPriority | None = Query(None, description="Filter by task priority"),
    assignee_id: int | None = Query(None, description="Filter by assignee ID"),
) -> dict:
    """Dependency to get task filtering parameters from query."""
    return {"status": status, "priority": priority, "assignee_id": assignee_id}