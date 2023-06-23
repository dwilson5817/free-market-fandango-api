from sqlalchemy.orm import Session

import models
import schemas
from crud import tags, price_changes


def get_stock(db: Session, stock_id: int):
    return db.query(models.Stock).filter(models.Stock.id == stock_id).first()


def get_stock_by_code(db: Session, stock_code: str):
    return db.query(models.Stock).filter(models.Stock.code == stock_code).first()


def get_stocks(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Stock).offset(skip).limit(limit).all()


def create_stock(db: Session, stock: schemas.StockCreate):
    db_stock = models.Stock(code=stock.code, name=stock.name)
    db.add(db_stock)
    db.commit()
    db.refresh(db_stock)

    for tag_name in stock.tags.split(','):
        tags.create_stock_tag(db, db_stock=db_stock, tag_name=tag_name)

    price_changes.create_price_change(db, stock_code=db_stock.code, new_price=stock.price, reason="Initial Price")

    return db_stock


def update_stock_in_stock(db: Session, stock: models.Stock, in_stock: bool):
    stock.in_stock = in_stock
    db.commit()


def delete_stock(db: Session, stock: models.Stock):
    db.delete(stock)
    db.commit()
