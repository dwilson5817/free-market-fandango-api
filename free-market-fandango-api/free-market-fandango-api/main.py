from fastapi import FastAPI
from mangum import Mangum

from .routers import auth

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

app.include_router(auth.router)

handler = Mangum(app, lifespan="off")
