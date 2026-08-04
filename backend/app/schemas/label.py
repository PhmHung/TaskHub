from pydantic import BaseModel, ConfigDict, Field


class LabelBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=50)
    color: str | None = Field(None, pattern=r"^#[0-9a-fA-F]{6}$")


class LabelCreate(LabelBase):
    pass


class LabelUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=50)
    color: str | None = Field(None, pattern=r"^#[0-9a-fA-F]{6}$")


class LabelResponse(LabelBase):
    id: int
    project_id: int

    model_config = ConfigDict(from_attributes=True)