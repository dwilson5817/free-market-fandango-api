import random

from sqlalchemy import func, text, and_
from sqlalchemy.orm import Session

from models import Event, EventActivation, MarketActivation, utc_now
from schemas import EventCreate
from crud import settings, price_changes, tags, activations


def get_current_event(db: Session) -> Event | None:
    db_current_activation = activations.get_current_activation(db=db)

    if not db_current_activation:
        return None

    db_current_event = db.query(EventActivation).filter(and_(
        EventActivation.market_activation_id == db_current_activation.id, EventActivation.ends_at > utc_now())).first()

    if not db_current_event:
        return change_current_event(db=db, current_activation=db_current_activation)

    return db_current_event.event


def change_current_event(db: Session, current_activation: MarketActivation) -> Event | None:
    min_event_mins = settings.get_setting(db=db, setting=settings.Settings.NEWS_MIN_DURATION)
    max_event_mins = settings.get_setting(db=db, setting=settings.Settings.NEWS_MAX_DURATION)

    events = db.query(Event).all()
    activated_events = [event_activation.event for event_activation in current_activation.events]
    events_not_yet_activated = [event for event in events if event not in activated_events]

    if len(events_not_yet_activated) == 0:
        return None

    new_event = random.choice(tuple(events_not_yet_activated))
    new_event_duration_mins = random.randint(min_event_mins, max_event_mins)

    db_event_activation = EventActivation(market_activation_id=current_activation.id, event_id=new_event.id, ends_at=func.timestampadd(text('MINUTE'), new_event_duration_mins, utc_now()))

    db.add(db_event_activation)
    db.commit()
    db.refresh(db_event_activation)

    for stock_code in get_stocks_affected_by_event(event=new_event):
        price_changes.change_stock_price(db=db, stock_code=stock_code, min_pct=new_event.change_min, max_pct=new_event.change_max, reason="New Event")

    return db_event_activation.event


def get_stocks_affected_by_event(event: Event):
    result = set()

    for tag in event.tags:
        for stock in tag.tag.stocks:
            result.add(stock.stock.code)

    return result


def get_event(db: Session, event_id: int):
    return db.query(Event).filter(Event.id == event_id).first()


def get_events(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Event).offset(skip).limit(limit).all()


def create_event(db: Session, event: EventCreate):
    db_event = Event(title=event.title,
                            body=event.body,
                            breaking=event.breaking,
                            video_url=event.video_url,
                            change_min=event.change_min,
                            change_max=event.change_max)
    db.add(db_event)
    db.commit()
    db.refresh(db_event)

    for tag_name in event.tags.split(','):
        tags.create_event_tag(db, db_event=db_event, tag_name=tag_name)

    return db_event


def delete_event(db: Session, event: Event):
    db.delete(event)
    db.commit()
