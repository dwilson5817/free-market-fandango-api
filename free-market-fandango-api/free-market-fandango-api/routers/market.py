import datetime

from fastapi import APIRouter, Depends, HTTPException

from ..crud import market, card, event, stock
from ..dependencies import get_table, validate_jwt
from ..schemas import Market, MarketBalance, MarketPrice

router = APIRouter(
    prefix="/market",
    tags=["markets"],
    dependencies=[Depends(get_table)],
)


@router.get(
    "",
    responses={
        404: {"detail": "Not Found"},
    }
)
def read_active_market(table=Depends(get_table)) -> Market:
    current_market = market.read_active_market(table)

    if not current_market:
        raise HTTPException(status_code=404, detail="A market has never been opened")

    return current_market


@router.post(
    "",
    response_model=Market,
    dependencies=[Depends(validate_jwt)],
    responses={
        400: {"detail": "Bad Request"}
    },
)
def open_market(table=Depends(get_table)):
    active_market = market.read_active_market(table)

    if active_market is not None:
        current_market = market.read_market(table, active_market.uuid)

        if current_market.active:
            raise HTTPException(status_code=400, detail="A market is already open")

    cards = card.read_cards(table)

    if not cards:
        raise HTTPException(status_code=400, detail="No cards have been created")

    stocks = stock.read_stocks(table)

    if not stocks:
        raise HTTPException(status_code=400, detail="No stocks have been created")

    events = event.read_events(table)

    if not events:
        raise HTTPException(status_code=400, detail="No events have been created")

    return market.open_market(
        table,
        Market()
    )


@router.get(
    "/{market_uuid}",
    response_model=Market,
    responses={
        404: {"detail": "Not Found"},
    }
)
def read_market(market_uuid: str, table=Depends(get_table)):
    result = market.read_market(table, market_uuid)

    if not result:
        raise HTTPException(status_code=404, detail="Account does not exist")

    return result


@router.delete(
    "/{market_uuid}",
    dependencies=[Depends(validate_jwt)],
    responses={
        400: {"detail": "Bad Request"},
        404: {"detail": "Not Found"},
    },
)
def stop_market(market_uuid: str, table=Depends(get_table), ends_in: int | None = 0):
    current_market = market.read_market(table, market_uuid)

    if current_market is None:
        raise HTTPException(status_code=404, detail="Market not found")

    if not current_market.active:
        raise HTTPException(status_code=400, detail="Market already closed")

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
