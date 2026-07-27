from fastapi import APIRouter, HTTPException, status

from app.schemas.item import Item, ItemCreate

router = APIRouter()

# Fake database (in-memory)
fake_items_db = {
    1: {"id": 1, "name": "Item 1", "description": "Description for item 1"},
    2: {"id": 2, "name": "Item 2", "description": "Description for item 2"},
}


@router.post("/", response_model=Item, status_code=status.HTTP_201_CREATED)
def create_item(item: ItemCreate):
    """Tạo một item mới."""
    new_id = max(fake_items_db.keys() or [0]) + 1
    new_item = Item(id=new_id, **item.model_dump())
    fake_items_db[new_id] = new_item.model_dump()
    return new_item


@router.get("/", response_model=list[Item])
def read_items(skip: int = 0, limit: int = 10):
    """Lấy danh sách các item."""
    items = list(fake_items_db.values())
    return items[skip : skip + limit]


@router.get("/{item_id}", response_model=Item)
def read_item(item_id: int):
    """Lấy thông tin chi tiết của một item."""
    db_item = fake_items_db.get(item_id)
    if db_item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return db_item