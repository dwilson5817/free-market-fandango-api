from sqlalchemy.orm import Session

import models


def create_stock_tag(db: Session, db_stock: models.Stock, tag_name: str):
    db_tag = get_tag_by_name(db, tag_name=tag_name)

    db_stock_tag = models.StockTag(stock_code=db_stock.code, tag_id=db_tag.id)

    db.add(db_stock_tag)
    db.commit()
    db.refresh(db_stock_tag)

    return db_stock_tag


def create_event_tag(db: Session, db_event: models.Event, tag_name: str):
    db_tag = get_tag_by_name(db, tag_name=tag_name)

    db_event_tag = models.EventTag(event_id=db_event.id, tag_id=db_tag.id)

    db.add(db_event_tag)
    db.commit()
    db.refresh(db_event_tag)

    return db_event_tag


def get_tag_by_name(db: Session, tag_name: str):
    tag_name = tag_name.strip()
    db_tag = db.query(models.Tag).filter(models.Tag.name == tag_name).first()

    if db_tag:
        return db_tag

    return create_tag(db, tag_name)


def create_tag(db: Session, tag_name: str):
    db_tag = models.Tag(name=tag_name)
    db.add(db_tag)
    db.commit()
    db.refresh(db_tag)

    return db_tag

