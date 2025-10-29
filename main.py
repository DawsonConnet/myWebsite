from fastapi import FastAPI
from contextlib import asynccontextmanager
from db.session import create_db_and_tables, SessionDep
from api.v1.api import api_router

#Add this
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Load the DB
    create_db_and_tables()
    yield

#Modify our FastAPI app
app = FastAPI(lifespan=lifespan)

app.include_router(api_router, prefix="/api/v1")


#Define our routes
@app.get("/")
async def root():    
  return {"message": "Hello World"}