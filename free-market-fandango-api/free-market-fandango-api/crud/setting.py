from boto3.dynamodb.conditions import Key

from ..constants import Settings, setting_defaults
from ..schemas import Setting

KEY = "Setting"


def _item_to_model(item):
    return Setting(key=item["SK"], value=item["Value"])


def _setting_or_default(response, setting: Settings):
    stored_setting = next(
        (item for item in response["Items"] if item["SK"] == setting.value), None
    )

    return (
        Setting(key=setting.value, value=setting_defaults[setting])
        if stored_setting is None
        else _item_to_model(stored_setting)
    )


def read_settings(table):
    response = table.query(KeyConditionExpression=Key("PK").eq(KEY))

    return [_setting_or_default(response, setting) for setting in Settings]


def update_setting(batch, setting: Setting):
    batch.put_item(
        Item={
            "PK": KEY,
            "SK": setting.key.value,
            "Value": setting.value
        }
    )


def update_settings(table, settings: list[Setting]):
    with table.batch_writer() as batch:
        for setting in settings:
            update_setting(batch, setting)

    return settings
