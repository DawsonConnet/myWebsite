from sqlmodel import select, func, col
from api.v1.endpoints.users import get_current_active_user
from typing import Annotated
from fastapi import Depends, APIRouter, HTTPException, Response
from db.session import SessionDep
from db.models import Movie
from db.models import User as UserModel

router = APIRouter()

@router.get("/")
def get_all_movies(session: SessionDep, response: Response, perPage: int = 10, curPage: int = 1, searchTerm: str = ""):
    base_query = select(Movie)
    if searchTerm:
        base_query = base_query.where(col(Movie.name).ilike(f"%{searchTerm}%"))
    
    count_statement = select(func.count()).select_from(base_query.subquery())
    total_movies = session.exec(count_statement).one()
    
    offset_value = (curPage - 1) * perPage
    statement = base_query.offset(offset_value).limit(perPage)
    movies = session.exec(statement).all()
    
    response.headers["X-Total-Count"] = str(total_movies)
    return {"movies": movies, "count": len(movies)}

@router.get("/{movie_id}")
def get_movie(movie_id: int, session: SessionDep):
    movie = session.get(Movie, movie_id)
    if not movie:
        raise HTTPException(status_code=404, detail="movie not found")
    return movie

@router.get("/user/{user_id}")
def get_movies_by_user(user_id: int, session: SessionDep):
    statement = select(Movie).where(Movie.user_id == user_id)
    movies = session.exec(statement).all()
    return {"movies": movies, "count": len(movies)}

@router.get("/service/{service_id}")
def get_movies_by_service(service_id: int, session: SessionDep):
    statement = select(Movie).where(Movie.service_id == service_id)
    movies = session.exec(statement).all()
    return {"movies": movies, "count": len(movies)}

@router.post("/", status_code=201)
def create_new_movie(movie: Movie, session: SessionDep, current_user: Annotated[UserModel, Depends(get_current_active_user)]):
    session.add(movie)
    session.commit()
    session.refresh(movie)
    return movie

@router.put("/{movie_id}")
def update_movie(movie_id: int, movie: Movie, session: SessionDep, current_user: Annotated[UserModel, Depends(get_current_active_user)]):
    db_movie = session.get(Movie, movie_id)
    if not db_movie:
        raise HTTPException(status_code=404, detail="Movie not found")
    
    db_movie.name = movie.name
    db_movie.altVersions = movie.altVersions
    db_movie.quality = movie.quality
    db_movie.user_id = movie.user_id
    db_movie.service_id = movie.service_id
    session.add(db_movie)
    session.commit()
    session.refresh(db_movie)
    return db_movie

@router.delete("/{movie_id}", status_code=204)
def delete_movie(movie_id: int, session: SessionDep, current_user: Annotated[UserModel, Depends(get_current_active_user)]):
    movie = session.get(Movie, movie_id)
    if not movie:
        raise HTTPException(status_code=404, detail="Movie not found")
    session.delete(movie)
    session.commit()
    return None