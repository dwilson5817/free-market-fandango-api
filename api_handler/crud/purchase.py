import datetime
import decimal

from boto3.dynamodb.conditions import Key

from ..constants import KeyComponents
from ..schemas import PurchaseOut
from ..utils import build_key, explode_key, notify_purchase_event


def _item_to_model(item):
    _, card_number, timestamp = explode_key(item["SK"])

    return PurchaseOut(
        price=item["Price"],
        stock_code=item["StockCode"],
        card_number=card_number,
        previous_balance=item["PreviousBalance"],
        timestamp=datetime.datetime.fromisoformat(timestamp),
    )


def read_purchases(table, market_uuid: str):
    response = table.query(
        KeyConditionExpression=(
                Key("PK").eq(build_key(KeyComponents.MARKET, market_uuid)) &
                Key("SK").begins_with(build_key(KeyComponents.PURCHASE))
        )
    )

    return [_item_to_model(item) for item in response["Items"]]


def read_purchases_by_card_number(table, market_uuid: str, card_number: int):
    response = table.query(
        KeyConditionExpression=(
                Key("PK").eq(build_key(KeyComponents.MARKET, market_uuid)) &
                Key("SK").begins_with(build_key(KeyComponents.PURCHASE, card_number))
        )
    )

    return [_item_to_model(item) for item in response["Items"]]


def create_purchase(table, market_uuid: str, purchase: PurchaseOut, new_balance: decimal.Decimal) -> PurchaseOut:
    with table.batch_writer() as batch:
        batch.put_item(
            Item={
                'PK': build_key(KeyComponents.MARKET, market_uuid),
                'SK': build_key(KeyComponents.CARD, purchase.card_number),
                'Balance': new_balance,
            }
        )

        table.put_item(
            Item={
                "PK": build_key(KeyComponents.MARKET, market_uuid),
                "SK": build_key(KeyComponents.PURCHASE, purchase.card_number, purchase.timestamp.isoformat()),
                "StockCode": purchase.stock_code,
                "PreviousBalance": purchase.previous_balance,
                "Price": purchase.price,
            }
        )

    notify_purchase_event(market_uuid, purchase.stock_code)

    return purchase
