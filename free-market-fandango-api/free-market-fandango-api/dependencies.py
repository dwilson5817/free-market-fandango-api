import os
from typing import Annotated

import boto3
from fastapi import HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from starlette import status

from .constants import ALGORITHM

table_name = os.environ["DYNAMODB_TABLE_ARN"]
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


async def validate_jwt(token: Annotated[str, Depends(oauth2_scheme)]):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        jwt.decode(token, os.environ["SECRET_KEY"], algorithms=[ALGORITHM])
    except JWTError:
        raise credentials_exception


def get_table():
    dynamodb = boto3.resource("dynamodb")

    table = dynamodb.Table(table_name)

    return table
