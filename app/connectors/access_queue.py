import boto3
from flask import json

email_queue_name = 'gov_uk_notify_email_queue'
sms_queue_name = 'gov_uk_notify_sms_queue'


def get_messages_from_queue(type):
    q = get_queue_for_type(type)
    return q.receive_messages(MessageAttributeNames=['type'], MaxNumberOfMessages=10)


def send_messages_to_queue(type, notifications):
    q = get_queue_for_type(type)
    for notification in notifications:
        q.send_message(MessageBody=json.dumps(notification.serialize()),
                       MessageAttributes={'type': {'StringValue': type, 'DataType': 'String'}})
    return True


def get_queue_for_type(type):
    if type == 'email':
        q = get_queue(email_queue_name)
    elif type == 'sms':
        q = get_queue(sms_queue_name)
    else:
        raise Exception("Invalid type for notification: {}".format(type))
    return q


def get_queue(name):
    return boto3.resource('sqs').create_queue(QueueName=name)
