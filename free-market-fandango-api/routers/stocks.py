from fastapi import APIRouter, Depends, HTTPException
from http.client import HTTPException
from sqlalchemy.orm import Session
from starlette import status

from schemas import Stock, StockCreate
from crud import stocks, price_changes, settings
from dependencies import get_db, validate_jwt

router = APIRouter()


@router.put("/crash/", status_code=204, dependencies=[Depends(validate_jwt)])
def crash_market(db: Session = Depends(get_db)):
    market_crash_loss = -settings.get_setting(db=db, setting=settings.Settings.MARKET_CRASH_LOSS)

    for db_stock in stocks.get_stocks(db=db):
        price_changes.change_stock_price(db=db, stock_code=db_stock.code, min_pct=market_crash_loss, max_pct=market_crash_loss, reason="Market Crash")


@router.put("/stocks/", response_model=Stock, dependencies=[Depends(validate_jwt)])
def create_stock(stock: StockCreate, db: Session = Depends(get_db)):
    db_stock = stocks.get_stock_by_code(db, stock_code=stock.code)

    if db_stock:
        raise HTTPException(status_code=400, detail="Stock code already in use!")

    return stocks.create_stock(db=db, stock=stock)


@router.get("/stocks/", response_model=list[Stock])
def read_stocks(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    db_stocks = stocks.get_stocks(db, skip=skip, limit=limit)

    for db_stock in db_stocks:
        if db_stock.in_stock:
            price_changes.check_for_no_purchase(db=db, stock=db_stock)

    return db_stocks


@router.put("/stocks/{stock_code}/", response_model=Stock, dependencies=[Depends(validate_jwt)])
def read_stock(stock_code: str, in_stock: bool = True, db: Session = Depends(get_db)):
    db_stock = stocks.get_stock_by_code(db, stock_code=stock_code)

    if db_stock is None:
        raise HTTPException(status_code=404, detail="Stock not found")

    stocks.update_stock_in_stock(db=db, stock=db_stock, in_stock=in_stock)

    return db_stock


@router.delete("/stocks/{stock_code}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(validate_jwt)])
def delete_stock(stock_code: str, db: Session = Depends(get_db)):
    db_stock = stocks.get_stock_by_code(db=db, stock_code=stock_code)

    if not db_stock:
        raise HTTPException(status_code=404, detail="Stock not found")

    stocks.delete_stock(db=db, stock=db_stock)
