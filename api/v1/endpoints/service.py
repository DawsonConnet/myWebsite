
from select import select
from fastapi import APIRouter, HTTPException
from db.session import SessionDep
from db.models import Service

router = APIRouter()

@router.get("/")
def get_all_services(session: SessionDep):
    statement = select(Service)
    services = session.exec(statement).all()
    return {"services": services, "count": len(services)}

@router.get("/{service_id}")
def get_service(service_id:int,session: SessionDep):
    service = session.get(service, service_id)
    if not service:
        raise HTTPException(status_code=404, detail="service not found")
    return service

@router.post("/", status_code=204)
def create_new_service(service: Service, session: SessionDep):
    session.add(service)
    session.commit()
    session.refresh(service)
    return service

@router.put("/{service_id}")
def update_service(service_id: int, service: Service, session: SessionDep):
    db_service = session.get(service, service_id)
    db_service.name = service.name
    session.add(db_service)
    session.commit()
    session.refresh(db_service)
    return db_service

@router.delete("/{service_id}", status_code=204)
def delete_service(service_id: int, session: SessionDep):
    service = session.get(service, service_id)
    session.delete(service)
    session.commit()
    return None