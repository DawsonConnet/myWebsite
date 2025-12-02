from sqlmodel import select, func, col
from fastapi import APIRouter, HTTPException, Response, status, Depends
from db.session import SessionDep, get_session
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta, timezone
from typing import Annotated
import jwt
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jwt.exceptions import InvalidTokenError
from pwdlib import PasswordHash
from pydantic import BaseModel
from db.models import User as UserModel

load_dotenv()

SECRET_KEY = os.getenv('SECRET_KEY')
ALGORITHM = os.getenv('ALGORITHM')
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv('ACCESS_TOKEN_EXPIRE_MINUTES', 30))

router = APIRouter()

class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None


class UserResponse(BaseModel):
    id: int
    username: str
    email: str | None = None
    full_name: str | None = None
    disabled: bool | None = None

class UserCreate(BaseModel):
    username: str
    email: str | None = None
    full_name: str | None = None
    password: str
    disabled: bool | None = False

class UserUpdate(BaseModel):
    username: str | None = None
    email: str | None = None
    full_name: str | None = None
    password: str | None = None

class UserInDB(UserResponse):
    hashed_password: str


password_hash = PasswordHash.recommended()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/users/token")


def verify_password(plain_password, hashed_password):
    return password_hash.verify(plain_password, hashed_password)


def get_password_hash(password):
    return password_hash.hash(password)


def get_user(session: SessionDep, username: str):
    user = session.exec(select(UserModel).where(UserModel.username == username)).first()
    return user

def authenticate_user(session: SessionDep, username: str, password: str):
    user = get_user(session, username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)], session: SessionDep):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except InvalidTokenError:
        raise credentials_exception
    user = get_user(session, username=token_data.username)
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(
    current_user: Annotated[UserModel, Depends(get_current_user)],
):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


@router.post("/token")
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    session: SessionDep
) -> Token:
    user = authenticate_user(session, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return Token(access_token=access_token, token_type="bearer")


@router.get("/me/", response_model=UserResponse)
async def read_users_me(
    current_user: Annotated[UserModel, Depends(get_current_active_user)],
):
    return current_user


@router.get("/me/items/")
async def read_own_items(
    current_user: Annotated[UserModel, Depends(get_current_active_user)],
):
    return [{"item_id": "Foo", "owner": current_user.username}]

@router.get("/")
def get_all_users(session: SessionDep, response: Response, perPage: int = 10, curPage: int = 1, searchTerm: str = ""):
    base_query = select(UserModel)
    if searchTerm:
        base_query = base_query.where(col(UserModel.username).ilike(f"%{searchTerm}%"))
    count_statement = select(func.count()).select_from(base_query.subquery())
    total_users = session.exec(count_statement).one()
    offset_value = (curPage - 1) * perPage
    statement = base_query.offset(offset_value).limit(perPage)
    users = session.exec(statement).all()
    response.headers["X-Total-Count"] = str(total_users)
    return {"users": users, "count": len(users)}

@router.get("/{user_id}")
def get_user_by_id(user_id: int, session: SessionDep):
    user = session.get(UserModel, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.post("/", status_code=201)
def create_new_user(user: UserCreate, session: SessionDep):
    existing_user = session.exec(
        select(UserModel).where(UserModel.username == user.username)
    ).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already exists")
    
    hashed_password = get_password_hash(user.password)
    db_user = UserModel(
        username=user.username,
        email=user.email,
        full_name=user.full_name,
        hashed_password=hashed_password,
        disabled=user.disabled or False
    )
    
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user

@router.put("/{user_id}")
def update_user(
    user_id: int, 
    user: UserUpdate, 
    session: SessionDep,
    current_user: Annotated[UserModel, Depends(get_current_active_user)]
):
    db_user = session.get(UserModel, user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if db_user.id != current_user.id:
        raise HTTPException(status_code=403, detail="You can only update your own profile")
    
    if user.username is not None:
        existing_user = session.exec(
            select(UserModel).where(
                UserModel.username == user.username,
                UserModel.id != user_id
            )
        ).first()
        if existing_user:
            raise HTTPException(status_code=400, detail="Username already exists")
        db_user.username = user.username
    
    if user.email is not None:
        db_user.email = user.email
    
    if user.full_name is not None:
        db_user.full_name = user.full_name
    
    if user.password is not None:
        db_user.hashed_password = get_password_hash(user.password)
    
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user

@router.delete("/{user_id}", status_code=204)
def delete_user(
    user_id: int, 
    session: SessionDep,
    current_user: Annotated[UserModel, Depends(get_current_active_user)]
):
    user = session.get(UserModel, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if user.id != current_user.id:
        raise HTTPException(status_code=403, detail="You can only delete your own account")
    
    session.delete(user)
    session.commit()
    return None