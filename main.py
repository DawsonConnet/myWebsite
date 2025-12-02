from contextlib import asynccontextmanager
from db.session import create_db_and_tables
from api.v1.api import api_router
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://10.120.1.21:5173", "http://10.120.1.21:5173"],  
    allow_credentials=True,
    allow_methods=["*"],  
    allow_headers=["*"],  
    expose_headers=["X-Total-Count"],
)

app.include_router(api_router, prefix="/api/v1") 

@app.get("/")
async def root():    
  return {"message": "Hello World"}