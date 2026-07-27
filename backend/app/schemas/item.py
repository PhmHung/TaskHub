from pydantic import BaseModel, ConfigDict


class ItemBase(BaseModel):
    """Schema cơ bản cho một item."""
    name: str
    description: str | None = None


class ItemCreate(ItemBase):
    """Schema để tạo một item mới."""
    pass


class Item(ItemBase):
    """Schema để trả về dữ liệu item, bao gồm cả ID."""
    id: int
    model_config = ConfigDict(from_attributes=True)