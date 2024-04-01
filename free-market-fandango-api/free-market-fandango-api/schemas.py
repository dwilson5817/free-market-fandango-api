from pydantic import BaseModel


class Auth(BaseModel):
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str
