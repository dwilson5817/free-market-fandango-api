from sqlalchemy.orm import Session

import models
import schemas
from crud import price_changes, accounts, settings


def get_purchase(db: Session, purchase_id: int):
    return db.query(models.Purchase).filter(models.Purchase.id == purchase_id).first()


def get_purchases(db: Session, skip: int = 0, limit: int = 100):
    response = db.query(models.Purchase).offset(skip).limit(limit).all()

    for purchase in response:
        print(purchase.purchased_at)

    return db.query(models.Purchase).offset(skip).limit(limit).all()


def create_purchase(db: Session, purchase: schemas.PurchaseCreate):
    # Race conditions?
    db_current_price = price_changes.get_current_price(db=db, stock_code=purchase.stock_code)

    db_purchase = models.Purchase(stock_code=purchase.stock_code, card_number=purchase.card_number, purchase_price=db_current_price)
    db.add(db_purchase)
    db.commit()
    db.refresh(db_purchase)

    account = accounts.get_account_by_card_number(db=db, card_number=purchase.card_number)
    account.balance = account.balance - db_current_price
    db.commit()

    min_pct = settings.get_setting(db=db, setting=settings.Settings.STOCK_PURCHASE_MIN_INCREASE)
    max_pct = settings.get_setting(db=db, setting=settings.Settings.STOCK_PURCHASE_MAX_INCREASE)

    price_changes.change_stock_price(db=db, stock_code=purchase.stock_code, min_pct=min_pct, max_pct=max_pct, reason="Purchase")

    return db_purchase
