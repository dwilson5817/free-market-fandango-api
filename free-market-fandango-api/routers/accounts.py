from http.client import HTTPException

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from starlette import status

from ..crud import accounts
from ..dependencies import get_db, validate_jwt
from ..schemas import Account, AccountCreate

router = APIRouter(
    prefix="/accounts",
    tags=["accounts"],
    dependencies=[Depends(get_db)],
    responses={404: {"description": "Not found"}},
)


@router.put("/", response_model=Account, dependencies=[Depends(validate_jwt)])
def create_user(account: AccountCreate, db: Session = Depends(get_db)):
    db_user = accounts.get_account_by_card_number(db, card_number=account.card_number)

    if db_user:
        raise HTTPException(status_code=400, detail="Card number already exists")

    return accounts.create_account(db=db, account=account)


@router.get("/", response_model=list[Account])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    db_accounts = accounts.get_accounts(db, skip=skip, limit=limit)

    return db_accounts


@router.get("/{card_number}", response_model=Account)
def read_user(card_number: int, db: Session = Depends(get_db)):
    db_account = accounts.get_account_by_card_number(db, card_number=card_number)

    if db_account is None:
        raise HTTPException(status_code=404, detail="Account not found")

    return db_account


@router.delete("/{card_number}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(validate_jwt)])
def delete_user(card_number: int, db: Session = Depends(get_db)):
    db_account = accounts.get_account_by_card_number(db=db, card_number=card_number)

    if not db_account:
        raise HTTPException(status_code=404, detail="Account not found")

    accounts.delete_account(db=db, account=db_account)
