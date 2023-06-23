from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

import schemas
from crud import activations
from dependencies import get_db, validate_jwt

router = APIRouter(
    prefix="/activation",
    tags=["activation"],
    dependencies=[Depends(get_db)],
    responses={404: {"description": "Not found"}},
)


@router.get("/", response_model=schemas.MarketActivation)
def read_status(db: Session = Depends(get_db)):
    db_market_activation = activations.get_current_activation(db=db)

    if not db_market_activation:
        raise HTTPException(status_code=404, detail="Market is not currently active")

    return activations.get_current_activation(db=db)


@router.put("/open/", response_model=schemas.MarketActivation, dependencies=[Depends(validate_jwt)])
def start_market(db: Session = Depends(get_db)):
    return activations.create_activation(db=db)


@router.put("/close/", response_model=schemas.MarketActivation, dependencies=[Depends(validate_jwt)])
def stop_market(ends_in: int, db: Session = Depends(get_db)):
    db_market_activation = activations.get_current_activation(db=db)

    if not db_market_activation:
        raise HTTPException(status_code=404, detail="Market is not currently active")

    return activations.update_activation(db=db, market_activation=db_market_activation, ends_in=ends_in)
