import os
from uuid import uuid4

import boto3


_JOIN_SYMBOL = '#'

_sqs = boto3.client('sqs')
_queue_url = os.environ["SQS_QUEUE_URL"]


def build_key(*args):
    components = [str(component) for component in args]

    return _JOIN_SYMBOL.join(components)


def explode_key(key: str):
    return key.split(_JOIN_SYMBOL)


def find_setting_value(current_settings, search_key):
    return next((setting for setting in current_settings if setting.key == search_key), None).value


def _send_sqs_message(message_body, message_attributes=None):
    return _sqs.send_message(
        QueueUrl=_queue_url,
        MessageAttributes={} if message_attributes is None else message_attributes,
        MessageBody=message_body,
        MessageGroupId='FreeMarketFandango',
        MessageDeduplicationId=str(uuid4())
    )


def notify_purchase_event(market_uuid: str, stock_code: str):
    _send_sqs_message(
        'Purchase',
        {
            'MarketUUID': {
                'DataType': 'String',
                'StringValue': market_uuid
            },
            'StockCode': {
                'DataType': 'String',
                'StringValue': stock_code
            }
        }
    )


def notify_cache_invalid_event(table, market_uuid: str = None):
    if market_uuid is None:
        active_market = table.get_item(
            Key={
                'PK': 'Market',
                'SK': 'Active'
            }
        )

        if "Item" not in active_market:
            return

        market_uuid = active_market["Item"]["UUID"]

    _send_sqs_message(
        'CacheInvalid',
        {
            'MarketUUID': {
                'DataType': 'String',
                'StringValue': market_uuid
            },
        }
    )
