from typing import Generic, List, TypeVar

from pydantic import BaseModel

DataType = TypeVar("DataType")

class IPaginatedResponse(BaseModel, Generic[DataType]):
    total: int
    page: int
    size: int
    results: List[DataType]