from sqlmodel import select, func, col
from fastapi import APIRouter, HTTPException, Response, status, Depends
from db.session import SessionDep
from typing import Annotated
from pydantic import BaseModel
from db.models import Service as ServiceModel, User as UserModel
from api.v1.endpoints.users import get_current_active_user

router = APIRouter()

class ServiceCreate(BaseModel):
    name: str

class ServiceUpdate(BaseModel):
    name: str

@router.get("/")
def get_all_services(
    session: SessionDep, 
    response: Response, 
    perPage: int = 10, 
    curPage: int = 1, 
    searchTerm: str = ""
):
    base_query = select(ServiceModel)
    if searchTerm:
        base_query = base_query.where(col(ServiceModel.name).ilike(f"%{searchTerm}%"))
    
    total_services = session.exec(select(func.count()).select_from(base_query.subquery())).one()
    services = session.exec(base_query.offset((curPage - 1) * perPage).limit(perPage)).all()
    
    response.headers["X-Total-Count"] = str(total_services)
    return {"services": services, "count": len(services)}

@router.get("/{service_id}")
def get_service_by_id(service_id: int, session: SessionDep):
    service = session.get(ServiceModel, service_id)
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")
    return service

@router.post("/", status_code=201)
def create_new_service(
    service: ServiceCreate, 
    session: SessionDep,
    current_user: Annotated[UserModel, Depends(get_current_active_user)]
):
    existing_service = session.exec(
        select(ServiceModel).where(ServiceModel.name == service.name)
    ).first()
    if existing_service:
        raise HTTPException(status_code=400, detail="Service name already exists")
    
    db_service = ServiceModel(name=service.name)
    session.add(db_service)
    session.commit()
    session.refresh(db_service)
    return db_service

@router.put("/{service_id}")
def update_service(
    service_id: int, 
    service: ServiceUpdate, 
    session: SessionDep,
    current_user: Annotated[UserModel, Depends(get_current_active_user)]
):
    db_service = session.get(ServiceModel, service_id)
    if not db_service:
        raise HTTPException(status_code=404, detail="Service not found")
    
    existing_service = session.exec(
        select(ServiceModel).where(
            ServiceModel.name == service.name,
            ServiceModel.id != service_id
        )
    ).first()
    if existing_service:
        raise HTTPException(status_code=400, detail="Service name already exists")
    
    db_service.name = service.name
    session.add(db_service)
    session.commit()
    session.refresh(db_service)
    return db_service

@router.delete("/{service_id}", status_code=204)
def delete_service(
    service_id: int, 
    session: SessionDep,
    current_user: Annotated[UserModel, Depends(get_current_active_user)]
):
    service = session.get(ServiceModel, service_id)
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")
    
    session.delete(service)
    session.commit()
    return None