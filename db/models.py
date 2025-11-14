from sqlmodel import Field, SQLModel, Relationship
from typing import Optional


class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(index=True)
    email: str
    full_name: str
    movies: list["Movie"] = Relationship(back_populates="user")

class Movie(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    altVersions: bool = Field(default=False)
    quality: str
    user_id: Optional[int] = Field(default=None, foreign_key="user.id")
    service_id: Optional[int] = Field(default=None, foreign_key="service.id")
    user: Optional[User] = Relationship(back_populates="movies")
    service: Optional["Service"] = Relationship(back_populates="movies")

class Service(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    movies: list[Movie] = Relationship(back_populates="service")