from sqlalchemy.orm import Session

from ..models import Purchase
from ..schemas import PurchaseCreate
from ..crud import price_changes, accounts, settings


def get_purchase(db: Session, purchase_id: int):
    return db.query(Purchase).filter(Purchase.id == purchase_id).first()


def get_purchases(db: Session, skip: int = 0, limit: int = 100):
    response = db.query(Purchase).offset(skip).limit(limit).all()

    for purchase in response:
        print(purchase.purchased_at)

    return db.query(Purchase).offset(skip).limit(limit).all()


def create_purchase(db: Session, purchase: PurchaseCreate):
    # Race conditions?
    db_current_price = price_changes.get_current_price(db=db, stock_code=purchase.stock_code)

    db_purchase = Purchase(stock_code=purchase.stock_code, card_number=purchase.card_number, purchase_price=db_current_price)
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
