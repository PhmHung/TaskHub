from fastapi import APIRouter

router = APIRouter(tags=["Users"])


@router.get("/users/me")
async def get_me():
    return {"message": "Not implemented yet"}
