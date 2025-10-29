
from select import select
from fastapi import APIRouter, HTTPException
from db.session import SessionDep
from db.models import Movie

router = APIRouter()

@router.get("/")
def get_all_movies(session: SessionDep):
    statement = select(Movie)
    movies = session.exec(statement).all()
    return {"movie": movies, "count": len(movies)}

@router.get("/{movie_id}")
def get_movie(movie_id:int, session: SessionDep):
    movie = session.get(movie, movie_id)
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

@router.post("/", status_code=204)
def create_new_movie(movie: Movie, session: SessionDep):
    session.add(movie)
    session.commit()
    session.refresh(movie)
    return movie

@router.put("/{movie_id}")
def update_movie(movie_id: int, movie: Movie, session: SessionDep):
    db_movie = session.get(movie, movie_id)
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
def delete_movie(movie_id: int, session: SessionDep):
    movie = session.get(movie, movie_id)
    session.delete(movie)
    session.commit()
    return None