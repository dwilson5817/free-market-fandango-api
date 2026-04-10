from uuid import UUID

from boto3.dynamodb.conditions import Key

from ..schemas import EventIn, EventOut
from ..constants import KeyComponents
from ..utils import notify_cache_invalid_event


def _item_to_model(item):
    return EventOut(
        uuid=item["SK"],
        title=item["Title"],
        body=item["Body"],
        breaking=item["Breaking"],
        video_url=item["VideoURL"],
        change_min=item["ChangeMin"],
        change_max=item["ChangeMax"],
        tags=item["Tags"],
    )


def read_event(table, event_uuid: UUID):
    response = table.get_item(
        Key={
            "PK": KeyComponents.EVENT.value,
            "SK": str(event_uuid),
        }
    )

    if "Item" not in response:
        return None

    return _item_to_model(response["Item"])


def read_events(table):
    response = table.query(KeyConditionExpression=Key("PK").eq(KeyComponents.EVENT.value))

    return [_item_to_model(item) for item in response["Items"]]


def update_event(table, event_request: EventIn) -> EventOut:
    event = EventOut(**event_request.model_dump())

    table.put_item(
        Item={
            "PK": KeyComponents.EVENT.value,
            "SK": str(event.uuid),
            "Title": event.title,
            "Body": event.body,
            "Breaking": event.breaking,
            "VideoURL": event.video_url,
            "ChangeMin": event.change_min,
            "ChangeMax": event.change_max,
            "Tags": event.tags,
        }
    )

    return event


def delete_event(table, event_uuid: str):
    table.delete_item(
        Key={
            "PK": KeyComponents.EVENT.value,
            "SK": event_uuid,
        }
    )

    notify_cache_invalid_event(table)
