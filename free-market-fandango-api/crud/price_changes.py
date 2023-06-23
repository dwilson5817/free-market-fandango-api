import datetime
import random

from sqlalchemy.orm import Session

from models import PriceChange, Stock
from crud import settings, stocks, activations


def change_stock_price(db: Session, stock_code: str, min_pct: float, max_pct: float, reason: str):
    if not activations.get_current_activation(db=db):
        return

    initial_price = get_original_price(db=db, stock_code=stock_code)
    current_price = get_current_price(db=db, stock_code=stock_code)
    new_price = current_price + (random.uniform(float(min_pct) / 100,
                                                float(max_pct) / 100) * current_price)
    pct_change_from_init = ((new_price - initial_price) / initial_price) * 100
    max_pct_change_from_init = -settings.get_setting(db=db, setting=settings.Settings.STOCK_MAX_PERCENT_LOSS)

    if pct_change_from_init > max_pct_change_from_init:
        create_price_change(db=db, stock_code=stock_code, new_price=new_price, reason=reason)


def get_original_price(db: Session, stock_code: str) -> float:
    stock = stocks.get_stock_by_code(db=db, stock_code=stock_code)

    return stock.price_changes[0].new_price


def get_current_price(db: Session, stock_code: str):
    db_last_price_change = db.query(PriceChange).filter(PriceChange.stock_code == stock_code).order_by(
        PriceChange.changed_at.desc()).first()

    return db_last_price_change.new_price


def create_price_change(db: Session, stock_code: str, new_price: float, reason: str):
    db_price_change = PriceChange(stock_code=stock_code, new_price=round(new_price, 2), reason=reason)
    db.add(db_price_change)
    db.commit()
    db.refresh(db_price_change)

    return db_price_change


def check_for_no_purchase(db: Session, stock: Stock):
    last_purchase = stock.created_at
    last_price_change = stock.price_changes[-1].changed_at

    if stock.purchases:
        last_purchase = stock.purchases[-1].purchased_at

    stock_no_purchase_loss_time = settings.get_setting(db=db, setting=settings.Settings.STOCK_NO_PURCHASE_LOSS_TIME)
    last_change_after = datetime.datetime.now() - datetime.timedelta(minutes=stock_no_purchase_loss_time)

    if (last_purchase < last_change_after) and (last_price_change < last_change_after):
        stock_no_purchase_min_loss = -settings.get_setting(db=db, setting=settings.Settings.STOCK_NO_PURCHASE_MIN_LOSS)
        stock_no_purchase_max_loss = -settings.get_setting(db=db, setting=settings.Settings.STOCK_NO_PURCHASE_MAX_LOSS)

        change_stock_price(db=db, stock_code=stock.code, min_pct=stock_no_purchase_min_loss, max_pct=stock_no_purchase_max_loss, reason="No purchase")
