import datetime
from uuid import UUID

from boto3.dynamodb.conditions import Key

from .setting import read_settings, update_setting
from ..constants import KeyComponents
from ..schemas import Market, MarketBalance, MarketPrice
from ..utils import build_key, explode_key, notify_cache_invalid_event


def _item_to_model(item):
    return Market(
        uuid=UUID(item["UUID"]),
        opened_at=datetime.datetime.fromisoformat(item["OpenedAt"]),
        closed_at=datetime.datetime.fromisoformat(item["ClosedAt"]) if item["ClosedAt"] is not None else None,
        current_event=item["CurrentEvent"],
    )


def read_active_market(table):
    response = table.get_item(
        Key={
            "PK": KeyComponents.MARKET.value,
            "SK": KeyComponents.ACTIVE.value,
        }
    )

    if "Item" not in response:
        return None

    return _item_to_model(response['Item'])


def read_market(table, market_uuid: str):
    response = table.get_item(
        Key={
            'PK': build_key(KeyComponents.MARKET, market_uuid),
            'SK': KeyComponents.DETAILS.value,
        }
    )

    if "Item" not in response:
        return None

    return _item_to_model(response["Item"])


def read_market_balances(table, market_uuid: str):
    response = table.query(
        KeyConditionExpression=(
                Key("PK").eq(build_key(KeyComponents.MARKET, market_uuid)) &
                Key("SK").begins_with(KeyComponents.CARD.value)
        )
    )

    return [MarketBalance(card_number=explode_key(item['SK'])[1], balance=item['Balance']) for item in response["Items"]]


def read_market_balance(table, market_uuid: str, card_number: int):
    response = table.get_item(
        Key={
            'PK': build_key(KeyComponents.MARKET, market_uuid),
            'SK': build_key(KeyComponents.CARD, card_number),
        }
    )

    if "Item" not in response:
        return None

    return MarketBalance(card_number=card_number, balance=response["Item"]['Balance'])


def read_market_prices(table, market_uuid: str):
    response = table.query(
        KeyConditionExpression=(
                Key("PK").eq(build_key(KeyComponents.MARKET, market_uuid)) &
                Key("SK").begins_with(KeyComponents.STOCK.value)
        )
    )

    def get_stock_code(item):
        _, stock_code = explode_key(item['SK'])

        return stock_code

    return [MarketPrice(stock_code=get_stock_code(item), price=item['Price']) for item in response["Items"]]


def read_market_price(table, market_uuid: str, stock_code: str):
    response = table.get_item(
        Key={
            'PK': build_key(KeyComponents.MARKET, market_uuid),
            'SK': build_key(KeyComponents.STOCK, stock_code),
        }
    )

    if "Item" not in response:
        return None

    return MarketPrice(stock_code=stock_code, price=response["Item"]['Price'])


def open_market(table, market: Market):
    current_settings = read_settings(table)

    with table.batch_writer() as batch:
        # Ensure defaults are committed to DynamoDB, the cron and event handler modules require some settings.
        for setting in current_settings:
            update_setting(batch, setting)

        batch.put_item(
            Item={
                'PK': build_key(KeyComponents.MARKET, market.uuid),
                'SK': KeyComponents.DETAILS.value,
                'UUID': str(market.uuid),
                'OpenedAt': market.opened_at.isoformat(),
                'ClosedAt': market.closed_at if market.closed_at is None else market.closed_at.isoformat(),
                'CurrentEvent': market.current_event,
            }
        )

    notify_cache_invalid_event(table, str(market.uuid))

    return market


def update_market(table, market: Market):
    market_uuid = str(market.uuid)

    table.update_item(
        Key={
            'PK': build_key(KeyComponents.MARKET, market_uuid),
            'SK': KeyComponents.DETAILS.value,
        },
        AttributeUpdates={
            'ClosedAt': {
                'Value': market.closed_at.isoformat(),
                'Action': 'PUT'
            }
        }
    )

    table.update_item(
        Key={
            'PK': KeyComponents.MARKET.value,
            'SK': KeyComponents.ACTIVE.value,
        },
        AttributeUpdates={
            'ClosedAt': {
                'Value': market.closed_at.isoformat(),
                'Action': 'PUT'
            }
        }
    )

    return market
