from fastapi import FastAPI
from mangum import Mangum
from starlette.middleware.cors import CORSMiddleware

import models
from database import engine
from routers import accounts, activations, events, purchases, spotify, stocks, auth, settings

models.Base.metadata.create_all(bind=engine)

app = FastAPI()


origins = [
    "http://localhost.tiangolo.com",
    "https://localhost.tiangolo.com",
    "http://localhost",
    "http://localhost:8080",
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "https://free-market-fandango.dylanwilson.dev"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(accounts.router)
app.include_router(activations.router)
app.include_router(auth.router)
app.include_router(events.router)
app.include_router(purchases.router)
app.include_router(settings.router)
app.include_router(spotify.router)
app.include_router(stocks.router)

handler = Mangum(app, lifespan="off")
