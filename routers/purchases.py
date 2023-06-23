from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

import schemas
from crud import purchases
from dependencies import get_db, validate_jwt

router = APIRouter()


@router.post("/purchases/", response_model=schemas.Purchase, dependencies=[Depends(validate_jwt)])
def create_purchase(purchase: schemas.PurchaseCreate, db: Session = Depends(get_db)):
    return purchases.create_purchase(db=db, purchase=purchase)


@router.get("/purchases/", response_model=list[schemas.Purchase], dependencies=[Depends(validate_jwt)])
def read_purchases(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return purchases.get_purchases(db, skip=skip, limit=limit)
