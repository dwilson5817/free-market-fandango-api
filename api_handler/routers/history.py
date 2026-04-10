from fastapi import APIRouter, Depends

from ..crud import history
from ..dependencies import get_table
from ..schemas import PriceChange

router = APIRouter(
    prefix="/market/{market_uuid}/history",
    tags=["history"],
    dependencies=[Depends(get_table)],
)


@router.get(
    "/{stock_code}",
    response_model=list[PriceChange]
)
def read_price_history_for_stock(market_uuid: str, stock_code: str, table=Depends(get_table)):
    return history.read_price_history_by_stock_code(table, market_uuid, stock_code)


@router.get(
    "",
    response_model=list[PriceChange]
)
def read_price_history(market_uuid: str, table=Depends(get_table)):
    return history.read_price_history(table, market_uuid)
