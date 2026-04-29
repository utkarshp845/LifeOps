import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from auth import get_current_user
from database import get_db
from models.build import BuildProject
from models.user import User
from schemas.build import BuildProjectCreate, BuildProjectPatch, BuildProjectRead

router = APIRouter(prefix="/build", tags=["build"], dependencies=[Depends(get_current_user)])


@router.get("/projects", response_model=list[BuildProjectRead])
def list_projects(db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    return db.scalars(select(BuildProject).order_by(BuildProject.created_at.desc(), BuildProject.name.asc())).all()


@router.post("/projects", response_model=BuildProjectRead, status_code=status.HTTP_201_CREATED)
def create_project(payload: BuildProjectCreate, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    project = BuildProject(**payload.model_dump())
    db.add(project)
    db.commit()
    db.refresh(project)
    return project


@router.get("/projects/{project_id}", response_model=BuildProjectRead)
def get_project(project_id: uuid.UUID, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    project = db.get(BuildProject, project_id)
    if project is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    return project


@router.patch("/projects/{project_id}", response_model=BuildProjectRead)
def patch_project(
    project_id: uuid.UUID,
    payload: BuildProjectPatch,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    project = db.get(BuildProject, project_id)
    if project is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(project, key, value)
    db.commit()
    db.refresh(project)
    return project
