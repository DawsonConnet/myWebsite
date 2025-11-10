from sqlmodel import select, func
from fastapi import APIRouter, HTTPException, Response
from db.session import SessionDep
from db.models import User

router = APIRouter()

@router.get("/")
def get_all_users(session: SessionDep, response: Response, perPage: int = 10, curPage: int = 1):
    count_statement = select(func.count(User.id))
    total_users = session.exec(count_statement).one()
    offset_value = (curPage - 1) * perPage
    statement = select(User).order_by(User.id).offset(offset_value).limit(perPage)
    users = session.exec(statement).all()
    response.headers["X-Total-Count"] = str(total_users)
    return {"users": users, "count": len(users)}

#Create route for GET USER
@router.get("/{user_id}")
def get_user(user_id:int,session: SessionDep):
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.post("/", status_code=204)
def create_new_user(user: User, session: SessionDep):
    session.add(user)
    session.commit()
    session.refresh(user)
    return user

@router.put("/{user_id}")
def update_user(user_id: int, user: User, session: SessionDep):
    db_user = session.get(User, user_id)
    db_user.username = user.username
    db_user.email = user.email
    db_user.full_name = user.full_name
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user

@router.delete("/{user_id}", status_code=204)
def delete_user(user_id: int, session: SessionDep):
    user = session.get(User, user_id)
    session.delete(user)
    session.commit()
    return None