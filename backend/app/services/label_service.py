from sqlalchemy.ext.asyncio import AsyncSession

from app.core import exceptions
from app.models import Label, Project
from app.repositories.label_repository import LabelRepository
from app.schemas.label import LabelCreate, LabelResponse, LabelUpdate


class LabelService:
    def __init__(self, db: AsyncSession, label_repo: LabelRepository | None = None):
        self.db = db
        self.label_repo = label_repo or LabelRepository()

    async def create_label(
        self, *, project: Project, label_in: LabelCreate
    ) -> LabelResponse:
        label = await self.label_repo.create(
            self.db, obj_in=label_in, project_id=project.id
        )
        return LabelResponse.model_validate(label)

    async def get_labels_by_project(
        self, *, project: Project
    ) -> list[LabelResponse]:
        labels = await self.label_repo.get_multi_by_project(
            self.db, project_id=project.id
        )
        return [LabelResponse.model_validate(label) for label in labels]

    async def update_label(
        self, *, label: Label, label_in: LabelUpdate
    ) -> LabelResponse:
        if label.project_id != label_in.project_id:
             raise exceptions.http_400_exc("Cannot change the project of a label.")
        updated_label = await self.label_repo.update(
            self.db, db_obj=label, obj_in=label_in
        )
        return LabelResponse.model_validate(updated_label)

    async def delete_label(self, *, label: Label) -> None:
        await self.label_repo.delete(self.db, id=label.id)