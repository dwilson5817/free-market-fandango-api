from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..schemas import Purchase, PurchaseCreate
from ..crud import purchases
from ..dependencies import get_db, validate_jwt

router = APIRouter()


@router.post("/purchases/", response_model=Purchase, dependencies=[Depends(validate_jwt)])
def create_purchase(purchase: PurchaseCreate, db: Session = Depends(get_db)):
    return purchases.create_purchase(db=db, purchase=purchase)


@router.get("/purchases/", response_model=list[Purchase], dependencies=[Depends(validate_jwt)])
def read_purchases(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return purchases.get_purchases(db, skip=skip, limit=limit)
