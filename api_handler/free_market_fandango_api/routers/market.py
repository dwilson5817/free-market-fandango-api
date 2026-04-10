import datetime

from fastapi import APIRouter, Depends, HTTPException
from starlette import status

from ..crud import market, card, event, stock
from ..dependencies import get_table, validate_jwt
from ..schemas import Market, MarketBalance, MarketPrice, APIError

router = APIRouter(
    prefix="/market",
    tags=["markets"],
    dependencies=[Depends(get_table)],
)


@router.get(
    "",
    response_model=Market,
    responses={
        404: {
            "description": "A market has never been opened",
            "model": APIError,
        },
    }
)
def read_active_market(table=Depends(get_table)):
    current_market = market.read_active_market(table)

    if not current_market:
        raise HTTPException(status_code=404, detail="A market has never been opened")

    return current_market


@router.post(
    "",
    dependencies=[Depends(validate_jwt)],
    response_model=Market,
    responses={
        400: {
            "description": "A market is already open or no cards, events or stocks have been created.",
            "model": APIError,
        },
        401: {
            "description": "Failed to validate credentials.",
            "model": APIError,
        }
    }
)
def open_market(table=Depends(get_table)):
    active_market = market.read_active_market(table)

    if active_market is not None:
        current_market = market.read_market(table, active_market.uuid)

        if current_market.active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="A market has never been opened"
            )

    cards = card.read_cards(table)

    if not cards:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No cards have been created"
        )

    stocks = stock.read_stocks(table)

    if not stocks:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No stocks have been created"
        )

    events = event.read_events(table)

    if not events:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No events have been created"
        )

    return market.open_market(
        table,
        Market()
    )


@router.get(
    "/{market_uuid}",
    response_model=Market,
    responses={
        404: {
            "description": "The requested market does not exist.",
            "model": APIError,
        },
    }
)
def read_market(market_uuid: str, table=Depends(get_table)):
    result = market.read_market(table, market_uuid)

    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="The requested market does not exist."
        )

    return result


@router.delete(
    "/{market_uuid}",
    dependencies=[Depends(validate_jwt)],
    response_model=Market,
    responses={
        400: {
            "description": "The market has already been closed.",
            "model": APIError,
        },
        401: {
            "description": "Failed to validate credentials.",
            "model": APIError,
        },
        404: {
            "description": "The requested market does not exist.",
            "model": APIError,
        },
    }
)
def stop_market(market_uuid: str, table=Depends(get_table), ends_in: int | None = 0):
    current_market = market.read_market(table, market_uuid)

    if current_market is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="The requested market does not exist."
        )

    if not current_market.active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The market has already been closed"
        )

    current_market.closed_at = datetime.datetime.now() + datetime.timedelta(minutes=ends_in)

    return market.update_market(table, current_market)


@router.get(
    "/{market_uuid}/price",
    response_model=list[MarketPrice]
)
def read_market_prices(market_uuid: str, table=Depends(get_table)):
    return market.read_market_prices(table, market_uuid)


@router.get(
    "/{market_uuid}/balance",
    response_model=list[MarketBalance]
)
def read_market_balances(market_uuid: str, table=Depends(get_table)):
    return market.read_market_balances(table, market_uuid)
