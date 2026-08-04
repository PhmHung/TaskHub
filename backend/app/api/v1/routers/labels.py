from fastapi import APIRouter, Depends, status

from app.api.dependencies.permissions import require_project_permission
from app.api.dependencies.resources import get_label_by_id
from app.api.dependencies.services import get_label_service
from app.core import exceptions
from app.models import Label, Project
from app.schemas.label import LabelCreate, LabelResponse, LabelUpdate
from app.services.label_service import LabelService

router = APIRouter(tags=["Labels"])


@router.post(
    "/",
    response_model=LabelResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new label for a project",
)
async def create_label(
    label_in: LabelCreate,
    project: Project = Depends(require_project_permission),
    service: LabelService = Depends(get_label_service),
):
    """
    Create a new label within a specific project.

    - User must be the project owner or a workspace OWNER/EDITOR.
    """
    return await service.create_label(project=project, label_in=label_in)


@router.get(
    "/", response_model=list[LabelResponse], summary="Get all labels for a project"
)
async def get_labels(
    project: Project = Depends(require_project_permission),
    service: LabelService = Depends(get_label_service),
):
    """
    Get all labels belonging to a specific project.

    - User must be a member of the workspace.
    """
    return await service.get_labels_by_project(project=project)


@router.put("/{label_id}", response_model=LabelResponse, summary="Update a label")
async def update_label(
    label_in: LabelUpdate,
    label: Label = Depends(get_label_by_id),
    project: Project = Depends(require_project_permission),
    service: LabelService = Depends(get_label_service),
):
    """
    Update a label's name or color.

    - User must be the project owner or a workspace OWNER/EDITOR.
    """
    if label.project_id != project.id:
        raise exceptions.http_404_exc("Label not found in this project.")
    return await service.update_label(label=label, label_in=label_in)


@router.delete(
    "/{label_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete a label"
)
async def delete_label(
    label: Label = Depends(get_label_by_id),
    project: Project = Depends(require_project_permission),
    service: LabelService = Depends(get_label_service),
):
    """
    Delete a label from a project.

    - User must be the project owner or a workspace OWNER/EDITOR.
    """
    if label.project_id != project.id:
        raise exceptions.http_404_exc("Label not found in this project.")
    await service.delete_label(label=label)