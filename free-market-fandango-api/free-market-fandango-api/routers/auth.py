import os
from datetime import timedelta
from http.client import HTTPException

from fastapi import APIRouter, HTTPException
from starlette import status

from ..constants import ACCESS_TOKEN_EXPIRE_MINUTES
from ..crud.auth import create_access_token
from ..schemas import Token, Auth

router = APIRouter(
    prefix="/auth",
    tags=["auth"],
)


@router.post(
    "",
    response_model=Token,
    responses={
        401: {"description": "Unauthorized"}
    },
)
async def request_access_token(auth: Auth):
    if auth.password != os.environ["ADMIN_PASSWORD"]:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            headers={
                "WWW-Authenticate": "Bearer"
            },
        )

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={}, expires_delta=access_token_expires)

    return Token(access_token=access_token)
