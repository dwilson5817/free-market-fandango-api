from fastapi import FastAPI
from mangum import Mangum

from .routers import auth

app = FastAPI()

app.include_router(auth.router)

handler = Mangum(app, lifespan="off")
