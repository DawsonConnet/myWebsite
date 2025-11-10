from fastapi import FastAPI
from contextlib import asynccontextmanager
from db.session import create_db_and_tables, SessionDep
from api.v1.api import api_router
from fastapi.middleware.cors import CORSMiddleware

#Add this
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Load the DB
    create_db_and_tables()
    yield

#Modify our FastAPI app
app = FastAPI(lifespan=lifespan)

# Allow requests from your Svelte frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://10.120.1.21:5173"],  # frontend origin
    allow_credentials=True,
    allow_methods=["*"],  # allow all HTTP methods
    allow_headers=["*"],  # allow all headers
    expose_headers=["X-Total-Count"],
)

app.include_router(api_router, prefix="/api/v1") 

#Define our routes
@app.get("/")
async def root():    
  return {"message": "Hello World"}