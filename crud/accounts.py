from sqlalchemy.orm import Session

import models
import schemas


def get_account(db: Session, account_id: int) -> models.Account:
    return db.query(models.Account).filter(models.Account.id == account_id).first()


def get_account_by_card_number(db: Session, card_number: int) -> models.Account:
    return db.query(models.Account).filter(models.Account.card_number == card_number).first()


def get_accounts(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Account).offset(skip).limit(limit).all()


def create_account(db: Session, account: schemas.AccountCreate):
    db_account = models.Account(card_number=account.card_number, name=account.name, balance=account.balance)
    db.add(db_account)
    db.commit()
    db.refresh(db_account)

    return db_account


def delete_account(db: Session, account: models.Account):
    db.delete(account)
    db.commit()
