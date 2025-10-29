from fastapi import APIRouter
from api.v1.endpoints import users, movie, service

api_router = APIRouter()

api_router.include_router(users.router, prefix="/users", tags=["Users"])

api_router.include_router(movie.router, prefix="/movies", tags=["Movies"])

api_router.include_router(service.router, prefix="/services", tags=["Services"])