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
        # First, check if a label with the same name already exists in the project.
        existing_label = await self.label_repo.get_by_name_and_project(
            self.db, name=label_in.name, project_id=project.id
        )
        if existing_label:
            raise exceptions.http_409_exc(
                f"Label with name '{label_in.name}' already exists in this project."
            )

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
        update_data = label_in.model_dump(exclude_unset=True)

        # If the name is being changed, check for conflicts within the same project.
        new_name = update_data.get("name")
        if new_name and new_name != label.name:
            existing_label = await self.label_repo.get_by_name_and_project(
                self.db, name=new_name, project_id=label.project_id
            )
            if existing_label:
                raise exceptions.http_409_exc(
                    f"A label with name '{new_name}' already exists in this project."
                )

        updated_label = await self.label_repo.update(
            self.db, db_obj=label, obj_in=update_data
        )
        return LabelResponse.model_validate(updated_label)

    async def delete_label(self, *, label: Label) -> None:
        await self.label_repo.delete(self.db, id=label.id)