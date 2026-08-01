from fastapi import Query


async def get_pagination_params(
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(20, ge=1, le=100, description="Page size"),
) -> dict[str, int]:
    return {"page": page, "size": size}