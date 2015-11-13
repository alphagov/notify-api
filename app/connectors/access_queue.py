import boto3
from flask import json

queueName = 'gov_uk_notify_queue'


def getMessagesFromQueue():
    q = getQueue(queueName)
    return q.receive_messages(MessageAttributeNames=['type'])


def sendMessagesToQueue(type, notifications):
    q = getQueue(queueName)

    for notification in notifications:
        q.send_message(MessageBody=json.dumps(notification),
                       MessageAttributes={'type': {'StringValue': type, 'DataType': 'String'}})


def getQueue(name):
    sqs = boto3.resource('sqs')
    q = sqs.get_queue_by_name(QueueName=name)
    return q
