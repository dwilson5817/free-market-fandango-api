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


@router.post("/", response_model=Token)
async def login_for_access_token(
    auth: Auth
):
    if auth.password != os.environ['ADMIN_PASSWORD']:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect admin password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={}, expires_delta=access_token_expires
    )

    return {"access_token": access_token, "token_type": "bearer"}
