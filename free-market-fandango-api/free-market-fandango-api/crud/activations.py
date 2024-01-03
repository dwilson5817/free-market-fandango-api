from sqlalchemy import or_, func, text
from sqlalchemy.orm import Session

from models import MarketActivation, utc_now


def create_activation(db: Session) -> MarketActivation:
    db_activation = MarketActivation()

    db.add(db_activation)
    db.commit()
    db.refresh(db_activation)

    return db_activation


def get_current_activation(db: Session) -> MarketActivation:
    db_market_activation = db.query(MarketActivation).filter(or_(MarketActivation.ends_at == None, MarketActivation.ends_at > utc_now())).first()

    return db_market_activation


def update_activation(db: Session, market_activation: MarketActivation, ends_in: int) -> MarketActivation:
    market_activation.ends_at = func.timestampadd(text('MINUTE'), ends_in, utc_now())
    db.commit()

    return market_activation
