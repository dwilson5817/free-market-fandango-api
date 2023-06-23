from sqlalchemy import or_, func, text
from sqlalchemy.orm import Session

import models


def create_activation(db: Session) -> models.MarketActivation:
    db_activation = models.MarketActivation()

    db.add(db_activation)
    db.commit()
    db.refresh(db_activation)

    return db_activation


def get_current_activation(db: Session) -> models.MarketActivation:
    db_market_activation = db.query(models.MarketActivation).filter(or_(models.MarketActivation.ends_at == None, models.MarketActivation.ends_at > models.utc_now())).first()

    return db_market_activation


def update_activation(db: Session, market_activation: models.MarketActivation, ends_in: int) -> models.MarketActivation:
    market_activation.ends_at = func.timestampadd(text('MINUTE'), ends_in, models.utc_now())
    db.commit()

    return market_activation
