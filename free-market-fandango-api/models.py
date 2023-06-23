from sqlalchemy import Column, Integer, String, Text, Boolean, ForeignKey, DateTime, Float
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.orm import relationship
from sqlalchemy.sql import expression

from database import Base


class utc_now(expression.FunctionElement):
    type = DateTime()
    inherit_cache = True


@compiles(utc_now, 'mariadb')
def mariadb_utcnow(element, compiler, **kw):
    return "UTC_TIMESTAMP()"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(Text)
    password_hashed = Column(Text)


class MarketActivation(Base):
    __tablename__ = "market_activations"

    id = Column(Integer, primary_key=True, index=True)
    started_at = Column(DateTime, server_default=utc_now())
    ends_at = Column(DateTime, nullable=True)

    events = relationship("EventActivation", back_populates="market_activation", cascade="all, delete-orphan")


class SpotifyToken(Base):
    __tablename__ = "spotify_tokens"

    id = Column(Integer, primary_key=True, index=True)
    access_token = Column(Text)
    token_type = Column(Text)
    expires_in = Column(Integer)
    scope = Column(Text)
    expires_at = Column(Integer)
    refresh_token = Column(Text)


class Setting(Base):
    __tablename__ = "settings"

    id = Column(Integer, primary_key=True, index=True)
    key = Column(String(50))
    value = Column(Integer)


class Account(Base):
    __tablename__ = "accounts"

    card_number = Column(Integer, primary_key=True, index=True)
    name = Column(String(50))
    balance = Column(Float, default=0.0)

    purchases = relationship("Purchase", back_populates="account", cascade="all, delete-orphan")


class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(Text)
    body = Column(Text)
    breaking = Column(Boolean, default=False)
    video_url = Column(Text, nullable=True)
    change_min = Column(Float)
    change_max = Column(Float)

    tags = relationship("EventTag", back_populates="event", cascade="all, delete-orphan")
    activations = relationship("EventActivation", back_populates="event", cascade="all, delete-orphan")


class Stock(Base):
    __tablename__ = "stocks"

    code = Column(String(5), primary_key=True, index=True)
    name = Column(String(50))
    in_stock = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=utc_now())

    tags = relationship("StockTag", back_populates="stock", cascade="all, delete-orphan")
    purchases = relationship("Purchase", back_populates="stock", cascade="all, delete-orphan")
    price_changes = relationship("PriceChange", back_populates="stock", cascade="all, delete-orphan")


class Tag(Base):
    __tablename__ = "tags"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True)

    stocks = relationship("StockTag", back_populates="tag")
    events = relationship("EventTag", back_populates="tag")


class StockTag(Base):
    __tablename__ = "stock_tags"

    id = Column(Integer, primary_key=True, index=True)
    stock_code = Column(String(50), ForeignKey("stocks.code"))
    tag_id = Column(Integer, ForeignKey("tags.id"))

    stock = relationship("Stock", back_populates="tags")
    tag = relationship("Tag", back_populates="stocks")


class EventTag(Base):
    __tablename__ = "event_tags"

    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(Integer, ForeignKey("events.id"))
    tag_id = Column(Integer, ForeignKey("tags.id"))

    event = relationship("Event", back_populates="tags")
    tag = relationship("Tag", back_populates="events")


class Purchase(Base):
    __tablename__ = "purchases"

    id = Column(Integer, primary_key=True, index=True)
    stock_code = Column(String(5), ForeignKey("stocks.code"))
    card_number = Column(Integer, ForeignKey("accounts.card_number"))
    purchase_price = Column(Float)
    purchased_at = Column(DateTime, server_default=utc_now())

    stock = relationship("Stock", back_populates="purchases")
    account = relationship("Account", back_populates="purchases")


class PriceChange(Base):
    __tablename__ = "price_changes"

    id = Column(Integer, primary_key=True, index=True)
    stock_code = Column(String(5), ForeignKey("stocks.code"))
    new_price = Column(Float)
    reason = Column(String(50))
    changed_at = Column(DateTime, server_default=utc_now())

    stock = relationship("Stock", back_populates="price_changes")


class EventActivation(Base):
    __tablename__ = "event_activations"

    id = Column(Integer, primary_key=True, index=True)
    market_activation_id = Column(Integer, ForeignKey("market_activations.id"))
    event_id = Column(Integer, ForeignKey("events.id"))
    started_at = Column(DateTime, server_default=utc_now())
    ends_at = Column(DateTime)

    market_activation = relationship("MarketActivation", back_populates="events")
    event = relationship("Event", back_populates="activations")
