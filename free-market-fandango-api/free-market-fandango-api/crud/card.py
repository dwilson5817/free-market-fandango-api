from boto3.dynamodb.conditions import Key

from ..schemas import Card
from ..constants import KeyComponents
from ..utils import notify_cache_invalid_event


def _item_to_model(item):
    return Card(card_number=item["SK"], name=item["Name"], balance=item["Balance"])


def read_card(table, card_number: int):
    response = table.get_item(
        Key={
            "PK": KeyComponents.CARD.value,
            "SK": str(card_number),
        }
    )

    if "Item" not in response:
        return None

    return _item_to_model(response["Item"])


def read_cards(table):
    response = table.query(
        KeyConditionExpression=Key("PK").eq(KeyComponents.CARD.value)
    )

    return [_item_to_model(item) for item in response["Items"]]


def update_card(table, card: Card):
    table.put_item(
        Item={
            "PK": KeyComponents.CARD.value,
            "SK": str(card.card_number),
            "Name": card.name,
            "Balance": card.balance,
        }
    )

    notify_cache_invalid_event(table)

    return card


def delete_card(table, card_number: int):
    table.delete_item(
        Key={
            "PK": KeyComponents.CARD.value,
            "SK": str(card_number),
        }
    )

    notify_cache_invalid_event(table)
