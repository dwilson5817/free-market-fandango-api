from enum import Enum


class Settings(Enum):
    NEWS_MIN_DURATION = "NewsMinDuration"
    NEWS_MAX_DURATION = "NewsMaxDuration"
    STOCK_MAX_PERCENT_LOSS = "StockMaxPercentLoss"
    STOCK_PURCHASE_MIN_INCREASE = "StockPurchaseMinIncrease"
    STOCK_PURCHASE_MAX_INCREASE = "StockPurchaseMaxIncrease"
    STOCK_NO_PURCHASE_MIN_LOSS = "StockNoPurchaseMinLoss"
    STOCK_NO_PURCHASE_MAX_LOSS = "StockNoPurchaseMaxLoss"
    STOCK_NO_PURCHASE_LOSS_TIME = "StockNoPurchaseLossTime"
    MARKET_CRASH_LOSS = "MarketCrashLoss"


class KeyComponents(Enum):
    def __str__(self):
        return str(self.value)

    MARKET = 'Market'
    ACTIVE = 'Active'
    CARD = 'Card'
    STOCK = 'Stock'
    PURCHASE = 'Purchase'
    DETAILS = 'Details'
    PRICE = 'Price'
    EVENT = 'Event'


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


ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 360
