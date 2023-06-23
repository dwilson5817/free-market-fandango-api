import datetime

from pydantic import BaseModel
from pydantic.types import constr


class User(BaseModel):
    username: str
    full_name: str | None = None


class TokenData(BaseModel):
    username: str | None = None


class UserInDB(User):
    hashed_password: str

    class Config:
        orm_mode = True


class SettingBase(BaseModel):
    pass


class SettingUpdate(SettingBase):
    settings: dict


class Setting(SettingBase):
    key: str
    value: int

    class Config:
        orm_mode = True


class MarketActivationBase(BaseModel):
    pass


class MarketActivation(BaseModel):
    started_at: datetime.datetime
    ends_at: datetime.datetime | None

    class Config:
        orm_mode = True


class AccountBase(BaseModel):
    card_number: int
    name: constr(min_length=1, max_length=50, strip_whitespace=True)


class AccountCreate(AccountBase):
    balance: float


class Account(AccountBase):
    balance: float

    class Config:
        orm_mode = True


class StockBase(BaseModel):
    code: constr(min_length=1, max_length=5, strip_whitespace=True)
    name: str


class StockCreate(StockBase):
    tags: str
    price: float


class Stock(StockBase):
    tags: list['StockTag'] = []
    price_changes: list['PriceChange'] = []
    in_stock: bool

    @property
    def initial_price(self) -> float:
        if len(self.price_changes) == 0:
            return -1

        return self.price_changes[0].new_price

    @property
    def price(self) -> float:
        if len(self.price_changes) == 0:
            return -1

        return self.price_changes[-1].new_price

    # Workaround for serializing properties with pydantic until
    # https://github.com/samuelcolvin/pydantic/issues/935
    # is solved
    @classmethod
    def get_properties(cls):
        return [prop for prop in dir(cls) if isinstance(getattr(cls, prop), property)]

    def dict(self, *args, **kwargs):
        self.__dict__.update(
            {prop: getattr(self, prop) for prop in self.get_properties()}
        )
        return super().dict(*args, **kwargs)

    def json(
        self,
        *args,
        **kwargs,
    ) -> str:
        self.__dict__.update(
            {prop: getattr(self, prop) for prop in self.get_properties()}
        )

        return super().json(*args, **kwargs)

    class Config:
        orm_mode = True


class EventBase(BaseModel):
    title: constr(min_length=1, max_length=50, strip_whitespace=True)
    body: str
    breaking: bool
    video_url: str | None
    change_min: float
    change_max: float


class EventCreate(EventBase):
    tags: str


class Event(EventBase):
    id: int
    tags: list['EventTag'] = []

    class Config:
        orm_mode = True


class PlaceholderValue(BaseModel):
    id: int
    placeholder_id: int
    value: constr(min_length=1, max_length=50, strip_whitespace=True)

    class Config:
        orm_mode = True


class PlaceholderBase(BaseModel):
    name: constr(min_length=1, max_length=50, strip_whitespace=True)


class PlaceholderCreate(PlaceholderBase):
    values: str


class Placeholder(PlaceholderBase):
    id: int
    values: list[PlaceholderValue] = []

    class Config:
        orm_mode = True


class TagBase(BaseModel):
    id: int
    name: constr(min_length=1, max_length=50, strip_whitespace=True)


class Tag(TagBase):
    class Config:
        orm_mode = True


class StockTagBase(BaseModel):
    tag: Tag


class StockTag(StockTagBase):
    class Config:
        orm_mode = True


class EventTagBase(BaseModel):
    tag: Tag


class EventTag(EventTagBase):
    class Config:
        orm_mode = True


class SettingBase(BaseModel):
    key: constr(min_length=1, max_length=50, strip_whitespace=True)


class SettingCreate(SettingBase):
    value: constr(min_length=1, max_length=50, strip_whitespace=True)


class PurchaseBase(BaseModel):
    pass


class PurchaseCreate(PurchaseBase):
    stock_code: constr(min_length=1, max_length=5, strip_whitespace=True)
    card_number: int


class Purchase(PurchaseBase):
    id: int
    stock: Stock
    account: Account
    purchase_price: float
    purchased_at: datetime.datetime

    class Config:
        orm_mode = True


class PriceChangeBase(BaseModel):
    pass


class PriceChange(PriceChangeBase):
    id: int
    new_price: float
    reason: str
    changed_at = datetime.datetime

    class Config:
        orm_mode = True


class Token(BaseModel):
    access_token: str
    token_type: str


class Auth(BaseModel):
    password: str


Stock.update_forward_refs()
Event.update_forward_refs()
