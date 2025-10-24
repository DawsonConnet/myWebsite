from fastapi import FastAPI
from contextlib import asynccontextmanager
from db.session import create_db_and_tables, SessionDep

#Add this
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Load the DB
    create_db_and_tables()
    yield

#Modify our FastAPI app
app = FastAPI(lifespan=lifespan)


#Start the app
app = FastAPI()

#Define our routes
@app.get("/")
async def root():    
  return {"message": "Hello World"}