import os
from datetime import timedelta, datetime
from jose import jwt

from ..constants import ALGORITHM


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    now = datetime.utcnow()
    expire = now + expires_delta if expires_delta else now + timedelta(minutes=15)

    to_encode.update({"exp": expire})

    return jwt.encode(to_encode, os.environ["SECRET_KEY"], algorithm=ALGORITHM)
