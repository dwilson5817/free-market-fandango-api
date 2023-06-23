from sqlalchemy.orm import Session

from ..models import Stock, StockTag, Event, EventTag, Tag


def create_stock_tag(db: Session, db_stock: Stock, tag_name: str):
    db_tag = get_tag_by_name(db, tag_name=tag_name)

    db_stock_tag = StockTag(stock_code=db_stock.code, tag_id=db_tag.id)

    db.add(db_stock_tag)
    db.commit()
    db.refresh(db_stock_tag)

    return db_stock_tag


def create_event_tag(db: Session, db_event: Event, tag_name: str):
    db_tag = get_tag_by_name(db, tag_name=tag_name)

    db_event_tag = EventTag(event_id=db_event.id, tag_id=db_tag.id)

    db.add(db_event_tag)
    db.commit()
    db.refresh(db_event_tag)

    return db_event_tag


def get_tag_by_name(db: Session, tag_name: str):
    tag_name = tag_name.strip()
    db_tag = db.query(Tag).filter(Tag.name == tag_name).first()

    if db_tag:
        return db_tag

    return create_tag(db, tag_name)


def create_tag(db: Session, tag_name: str):
    db_tag = Tag(name=tag_name)
    db.add(db_tag)
    db.commit()
    db.refresh(db_tag)

    return db_tag

