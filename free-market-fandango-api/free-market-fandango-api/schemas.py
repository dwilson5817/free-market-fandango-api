import datetime
import decimal
from typing import Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, constr, Field, computed_field, model_validator
from .constants import Settings


class Auth(BaseModel):
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class APIError(BaseModel):
    message: str


class Card(BaseModel):
    card_number: int
    name: constr(min_length=1, max_length=50, strip_whitespace=True)
    balance: decimal.Decimal


class EventIn(BaseModel):
    title: constr(min_length=1, max_length=50, strip_whitespace=True)
    body: str
    breaking: bool
    video_url: Optional[str] = None
    change_min: decimal.Decimal
    change_max: decimal.Decimal
    tags: list[str] = []

    @model_validator(mode='after')
    def video_url_required_when_breaking(self):
        if self.breaking and not self.video_url:
            raise ValueError('video_url is required when breaking is true')
        return self


class EventOut(EventIn):
    uuid: UUID = Field(default_factory=uuid4)


class Market(BaseModel):
    uuid: UUID = Field(default_factory=uuid4)
    opened_at: datetime.datetime = Field(default_factory=datetime.datetime.now)
    closed_at: datetime.datetime | None = None
    current_event: str | None = None

    @computed_field
    @property
    def active(self) -> bool:
        return (
            datetime.datetime.now() < self.closed_at
            if self.closed_at is not None
            else True
        )


class MarketBalance(BaseModel):
    card_number: int
    balance: decimal.Decimal


class MarketPrice(BaseModel):
    stock_code: str
    price: decimal.Decimal


class PriceChange(BaseModel):
    stock_code: str
    previous_price: decimal.Decimal
    reason: str
    timestamp: datetime.datetime


class PurchaseIn(BaseModel):
    price: decimal.Decimal
    stock_code: str
    card_number: int


class PurchaseOut(PurchaseIn):
    previous_balance: decimal.Decimal = 0
    timestamp: datetime.datetime = Field(default_factory=datetime.datetime.now)


class Setting(BaseModel):
    key: Settings
    value: int


class Stock(BaseModel):
    code: constr(min_length=1, max_length=5, strip_whitespace=True)
    name: str
    tags: list[str] = []
    initial_price: decimal.Decimal
