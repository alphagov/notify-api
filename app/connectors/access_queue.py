import boto3
from flask import json

queueName = 'gov_uk_notify_queue'


def get_messages_from_queue():
    q = get_queue(queueName)
    return q.receive_messages(MessageAttributeNames=['type'], MaxNumberOfMessages=10)


def send_messages_to_queue(type, notifications):
    q = get_queue(queueName)
    for notification in notifications:
        q.send_message(MessageBody=json.dumps(notification.serialize()),
                       MessageAttributes={'type': {'StringValue': type, 'DataType': 'String'}})
    return True


def get_queue(name):
    return boto3.resource('sqs').create_queue(QueueName=name)
