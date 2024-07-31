from fastapi import APIRouter, Depends, HTTPException

from ..crud import market, purchase
from ..dependencies import get_table, validate_jwt
from ..schemas import PurchaseIn, PurchaseOut, APIError

router = APIRouter(
    prefix="/market/{market_uuid}/purchase",
    tags=["purchases"],
    dependencies=[Depends(get_table)],
    responses={
        400: {"description": "Bad Request"},
        404: {"description": "Not Found"},
    },
)


@router.get(
    "/{card_number}",
    response_model=list[PurchaseOut]
)
def read_purchases_for_card(market_uuid: str, card_number: int, table=Depends(get_table)):
    return purchase.read_purchases_by_card_number(table, market_uuid, card_number)


@router.post(
    "",
    response_model=PurchaseOut,
    dependencies=[Depends(validate_jwt)],
    responses={
        400: {
            "description": "Market is closed, stock price has changed or card has insufficient balance.",
            "model": APIError,
        },
        401: {
            "description": "Failed to validate credentials.",
            "model": APIError,
        },
        404: {
            "description": "Market, stock or card does not exist.",
            "model": APIError,
        },
    },
)
def create_purchase(market_uuid: str, new_purchase: PurchaseIn, table=Depends(get_table)):
    current_market = market.read_market(table, market_uuid)

    if not current_market:
        raise HTTPException(status_code=404, detail="Market does not exist")

    if not current_market.active:
        raise HTTPException(status_code=400, detail="Market is closed")

    stock_price = market.read_market_price(table, market_uuid, new_purchase.stock_code)

    if not stock_price:
        raise HTTPException(status_code=404, detail="Stock does not exist")

    if stock_price.price != new_purchase.price:
        raise HTTPException(status_code=400, detail="Stock price has changed, please refresh and submit again")

    card_balance = market.read_market_balance(table, market_uuid, new_purchase.card_number)

    if card_balance is None:
        raise HTTPException(status_code=404, detail="Card does not exist")

    purchase_out = PurchaseOut(
        **new_purchase.model_dump(),
        previous_balance=card_balance.balance
    )

    new_balance = card_balance.balance - new_purchase.price

    if new_balance < 0:
        raise HTTPException(status_code=400, detail="Insufficient card balance")

    return purchase.create_purchase(table, market_uuid, purchase_out, new_balance)
