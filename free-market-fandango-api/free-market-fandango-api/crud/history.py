import datetime

from boto3.dynamodb.conditions import Key

from ..utils import build_key, explode_key
from ..constants import KeyComponents
from ..schemas import PriceChange


def _item_to_model(item):
    _, stock_code, timestamp = explode_key(item["SK"])

    return PriceChange(
        stock_code=stock_code,
        previous_price=item["PreviousPrice"],
        reason=item["Reason"],
        timestamp=datetime.datetime.fromisoformat(timestamp),
    )


def read_price_history(table, market_uuid: str):
    response = table.query(
        KeyConditionExpression=(
                Key("PK").eq(build_key(KeyComponents.MARKET, market_uuid)) &
                Key("SK").begins_with(KeyComponents.PRICE.value)
        )
    )

    return [_item_to_model(item) for item in response["Items"]]


def read_price_history_by_stock_code(table, market_uuid: str, stock_code: str):
    response = table.query(
        KeyConditionExpression=(
                Key("PK").eq(build_key(KeyComponents.MARKET, market_uuid)) &
                Key("SK").begins_with(build_key(KeyComponents.PRICE, stock_code))
        )
    )

    return [_item_to_model(item) for item in response["Items"]]
