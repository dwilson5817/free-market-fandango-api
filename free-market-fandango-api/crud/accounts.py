from sqlalchemy.orm import Session

from models import Account
from schemas import AccountCreate


def get_account(db: Session, account_id: int) -> Account:
    return db.query(Account).filter(Account.id == account_id).first()


def get_account_by_card_number(db: Session, card_number: int) -> Account:
    return db.query(Account).filter(Account.card_number == card_number).first()


def get_accounts(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Account).offset(skip).limit(limit).all()


def create_account(db: Session, account: AccountCreate):
    db_account = Account(card_number=account.card_number, name=account.name, balance=account.balance)
    db.add(db_account)
    db.commit()
    db.refresh(db_account)

    return db_account


def delete_account(db: Session, account: Account):
    db.delete(account)
    db.commit()
