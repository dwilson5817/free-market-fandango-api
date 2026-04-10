from fastapi import APIRouter, Depends
from starlette import status
from starlette.exceptions import HTTPException

from ..crud import stock
from ..dependencies import get_table, validate_jwt
from ..schemas import Stock, APIError

router = APIRouter(
    prefix="/stock",
    tags=["stocks"],
    dependencies=[Depends(get_table)],

)


@router.get(
    "",
    response_model=list[Stock],
)
def read_stocks(table=Depends(get_table)):
    return stock.read_stocks(table)


@router.put(
    "",
    dependencies=[Depends(validate_jwt)],
    response_model=Stock,
    responses={
        401: {
            "description": "Failed to validate credentials.",
            "model": APIError,
        },
    },
)
def create_stock(stock_model: Stock, table=Depends(get_table)):
    return stock.create_stock(table, stock_model)


@router.get(
    "/{stock_code}",
    response_model=Stock,
    responses={
        401: {
            "description": "Failed to validate credentials.",
            "model": APIError,
        },
        404: {
            "description": "Stock does not exist.",
            "model": APIError,
        },
    },
)
def read_stock(stock_code: str, table=Depends(get_table)):
    response = stock.read_stock(table, stock_code)

    if not response:
        raise HTTPException(status_code=404, detail="Stock does not exist")

    return response


@router.delete(
    "/{stock_code}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(validate_jwt)],
    responses={
        401: {
            "description": "Failed to validate credentials.",
            "model": APIError,
        },
    }
)
def delete_stock(stock_code: str, table=Depends(get_table)):
    stock.delete_stock(table, stock_code)
