from typing import List
from fastapi import APIRouter, Path, status, Depends, HTTPException
from fastapi.responses import JSONResponse
from tasks import schemas
from tasks.schemas import TaskResponseSchema, TaskCreateSchema, TaskUpdateSchema
from tasks.models import TaskModel
from sqlalchemy.orm import Session
from core.database import get_db

from auth.jwt_auth import get_authenticated_user


router = APIRouter(tags=["tasks"], prefix="/tasks")


@router.get("/tasks", response_model=List[TaskResponseSchema])
async def retrieve_tasks_list(
    db: Session = Depends(get_db),
):
    result = query = db.query(TaskModel).all()
    return result


@router.get("/tasks/{task_id}", response_model=TaskResponseSchema)
async def retrieve_task_detail(
    task_id: int = Path(..., gt=0), db: Session = Depends(get_db)
):
    task_obj = db.query(TaskModel).filter_by(id=task_id).first()
    if not task_obj:
        raise HTTPException(status_code=404, detail="Task not found")
    return task_obj


@router.post("/tasks")  # ,response_model=TaskResponseSchema)
async def create_task(
    request: TaskCreateSchema,
    db: Session = Depends(get_db),
    user=Depends(get_authenticated_user),
):
    data = request.model_dump()
    data.update({"user_id": user.id})
    task_obj = TaskModel(**data)
    db.add(task_obj)
    db.commit()
    db.refresh(task_obj)
    return task_obj


@router.put("/tasks/{task_id}", response_model=TaskResponseSchema)
async def update_task(
    request: TaskUpdateSchema,
    task_id: int = Path(..., gt=0),
    db: Session = Depends(get_db),
):
    task_obj = db.query(TaskModel).filter_by(id=task_id).first()
    if not task_obj:
        raise HTTPException(status_code=404, detail="Task not found")

    # Update fields using setattr
    for field, value in request.model_dump(exclude_unset=True).items():
        setattr(task_obj, field, value)

    db.commit()  # Commit the changes to the database
    db.refresh(task_obj)  # Refresh the task object to reflect the updated data

    return task_obj  # Return the updated task object


@router.delete("/tasks/{task_id}", status_code=204)
async def delete_task(task_id: int = Path(..., gt=0), db: Session = Depends(get_db)):
    task_obj = db.query(TaskModel).filter_by(id=task_id).first()
    if not task_obj:
        raise HTTPException(status_code=404, detail="Task not found")
    db.delete(task_obj)
    db.commit()
