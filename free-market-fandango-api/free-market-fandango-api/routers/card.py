import os

from fastapi import APIRouter, Depends, HTTPException
from starlette.responses import Response
from starlette.status import HTTP_204_NO_CONTENT

from ..crud import card
from ..dependencies import get_table, validate_jwt
from ..schemas import Card

router = APIRouter(
    prefix="/card",
    tags=["cards"],
    dependencies=[Depends(get_table)],
)


@router.get(
    "",
    response_model=list[Card],
)
def read_cards(table=Depends(get_table)):
    print(os.environ)

    return card.read_cards(table)


@router.get(
    "/{card_number}",
    response_model=Card,
    responses={
        404: {"description": "Not Found"}
    }
)
def read_card(card_number: int, table=Depends(get_table)):
    user = card.read_card(table, card_number)

    if not user:
        raise HTTPException(status_code=404, detail="Card does not exist")

    return user


@router.put(
    "",
    response_model=Card,
    dependencies=[Depends(validate_jwt)],
)
def update_card(card_model: Card, table=Depends(get_table)):
    return card.update_card(table, card_model)


@router.delete("/{card_number}", dependencies=[Depends(validate_jwt)])
def delete_card(card_number: int, table=Depends(get_table)):
    card.delete_card(table, card_number)

    return Response(status_code=HTTP_204_NO_CONTENT)
