from enum import Enum

from sqlalchemy.orm import Session

from models import Setting


class Settings(Enum):
    NEWS_MIN_DURATION = 'NewsMinDuration'
    NEWS_MAX_DURATION = 'NewsMaxDuration'
    STOCK_MAX_PERCENT_LOSS = 'StockMaxPercentLoss'
    STOCK_PURCHASE_MIN_INCREASE = 'StockPurchaseMinIncrease'
    STOCK_PURCHASE_MAX_INCREASE = 'StockPurchaseMaxIncrease'
    STOCK_NO_PURCHASE_MIN_LOSS = 'StockNoPurchaseMinLoss'
    STOCK_NO_PURCHASE_MAX_LOSS = 'StockNoPurchaseMaxLoss'
    STOCK_NO_PURCHASE_LOSS_TIME = 'StockNoPurchaseLossTime'
    MARKET_CRASH_LOSS = 'MarketCrashLoss'


setting_defaults = {
    Settings.NEWS_MIN_DURATION: 10,
    Settings.NEWS_MAX_DURATION: 15,
    Settings.STOCK_MAX_PERCENT_LOSS: 80,
    Settings.STOCK_PURCHASE_MIN_INCREASE: 20,
    Settings.STOCK_PURCHASE_MAX_INCREASE: 30,
    Settings.STOCK_NO_PURCHASE_MIN_LOSS: 2,
    Settings.STOCK_NO_PURCHASE_MAX_LOSS: 5,
    Settings.STOCK_NO_PURCHASE_LOSS_TIME: 3,
    Settings.MARKET_CRASH_LOSS: 90,
}


def get_settings(db: Session) -> list[Setting]:
    return db.query(Setting).all()


def get_setting_model(db: Session, setting: Settings):
    return db.query(Setting).filter(Setting.key == setting.value).first()


def get_setting(db: Session, setting: Settings):
    db_setting = db.query(Setting).filter(Setting.key == setting.value).first()

    if not db_setting:
        return setting_defaults[setting]

    return db_setting.value


def set_setting(db: Session, setting: Settings, value: int):
    db_setting = db.query(Setting).filter(Setting.key == setting.value).first()

    if not value:
        delete_setting(db=db, setting=setting)
        return

    if not db_setting:
        return create_setting(db, setting, value)

    db_setting.value = value
    db.commit()
    db.refresh(db_setting)

    return db_setting


def create_setting(db: Session, setting: Settings, value: int):
    db_setting = Setting(key=setting.value, value=value)

    db.add(db_setting)
    db.commit()
    db.refresh(db_setting)

    return db_setting


def delete_setting(db: Session, setting: Settings):
    db_setting = get_setting_model(db=db, setting=setting)

    if not db_setting:
        return

    db.delete(db_setting)
    db.commit()
