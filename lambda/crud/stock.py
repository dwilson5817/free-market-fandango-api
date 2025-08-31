from boto3.dynamodb.conditions import Key

from ..schemas import Stock
from ..constants import KeyComponents
from ..utils import notify_cache_invalid_event


def _item_to_model(item) -> Stock:
    return Stock(
        code=item["SK"],
        name=item["Name"],
        initial_price=item["InitialPrice"],
        tags=item["Tags"],
    )


def read_stock(table, stock_code: str) -> Stock | None:
    response = table.get_item(
        Key={
            "PK": KeyComponents.STOCK.value,
            "SK": stock_code,
        }
    )

    if "Item" not in response:
        return None

    return _item_to_model(response["Item"])


def read_stocks(table) -> list[Stock]:
    response = table.query(
        KeyConditionExpression=Key("PK").eq(KeyComponents.STOCK.value)
    )

    return [_item_to_model(item) for item in response["Items"]]


def create_stock(table, stock: Stock) -> Stock:
    table.put_item(
        Item={
            "PK": KeyComponents.STOCK.value,
            "SK": stock.code,
            "Name": stock.name,
            "InitialPrice": stock.initial_price,
            "Tags": stock.tags,
        }
    )

    notify_cache_invalid_event(table)

    return stock


def delete_stock(table, stock_code: str) -> None:
    table.delete_item(
        Key={
            "PK": KeyComponents.STOCK.value,
            "SK": stock_code,
        }
    )

    notify_cache_invalid_event(table)
