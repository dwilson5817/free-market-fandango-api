from fastapi import FastAPI
from mangum import Mangum
from fastapi.middleware.cors import CORSMiddleware
from starlette.exceptions import HTTPException
from starlette.responses import JSONResponse

from .schemas import APIError
from .routers import auth, card, event, history, market, purchase, setting, stock

app = FastAPI(
    title="Free Market Fandango",
    summary="A stock market themed party where purchases affect drink prices. 🍹",
    contact={
        "name": "Dylan Wilson",
        "url": "https://dylanwilson.dev",
        "email": "mail@dylanwilson.dev",
    },
    license_info={
        "name": "GNU General Public License v3.0",
        "url": "https://gitlab.dylanw.dev/free-market-fandango/api/-/raw/main/LICENSE",
    },
)


origins = [
    "https://market.dylanw.dev",
    "http://localhost:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(card.router)
app.include_router(event.router)
app.include_router(history.router)
app.include_router(purchase.router)
app.include_router(market.router)
app.include_router(setting.router)
app.include_router(stock.router)


@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
            status_code=exc.status_code,
            content=APIError(message=exc.detail).model_dump()
        )


handler = Mangum(app, lifespan="off")
