from datetime import datetime

from flask import json
import moto
import boto3

from app.connectors.access_queue import send_messages_to_queue, get_messages_from_queue
from app.models import Notification, Job


notification = Notification(to='mock@example.com',
                            message='notification message',
                            status='created',
                            method='email',
                            created_at=datetime.utcnow(),
                            job=Job(id=1234, name='jobname',
                                    filename='filename',
                                    created_at=datetime.utcnow(), service_id=1234))


@moto.mock_sqs
def test_send_messages_to_queue_adds_message_queue(notify_api):
    q = set_up_mock_queue('email')
    q.send_message(MessageBody=json.dumps(notification.serialize()),
                   MessageAttributes={'type': {'StringValue': 'email', 'DataType': 'String'}})

    messages = [notification]
    b = send_messages_to_queue('email', messages)
    assert b is True


@moto.mock_sqs
def test_send_sms_messages_to_queue_adds_message_queue(notify_api):
    q = set_up_mock_queue('sms')
    sms = Notification(to='+441234512345',
                       message='hello world',
                       job_id=1234)
    q.send_message(MessageBody=json.dumps(sms.serialize()),
                   MessageAttributes={'type': {'StringValue': 'sms', 'DataType': 'String'}})

    messages = [notification]
    b = send_messages_to_queue('sms', messages)
    assert b is True


@moto.mock_sqs
def test_send_messages_to_queue_throws_exception_when_notification_is_badly_formed(notify_api):
    set_up_mock_queue('email')
    msg = {'to': 'jane@example.com',
           'from': 'stan@example.gov.uk',
           'subject': 'notification2 subject',
           'message': 'notification2 message'}

    messages = [msg]
    try:
        send_messages_to_queue('email', messages)
        assert False
    except AttributeError as e:
        assert True


@moto.mock_sqs
def test_get_messages_from_queue_returns_message_queue(notify_api):
    q = set_up_mock_queue('email')
    q.send_message(MessageBody=json.dumps(notification.serialize()),
                   MessageAttributes={'type': {'StringValue': 'email', 'DataType': 'String'}})

    messages = get_messages_from_queue('email')
    for m in messages:
        assert m.body == json.dumps(notification.serialize())


def set_up_mock_queue(type):
    boto3.setup_default_session(region_name='eu-west-1')
    conn = boto3.resource('sqs', region_name='eu-west-1')
    if type == 'email':
        name = 'gov_uk_notify_email_queue'
    else:
        name = 'gov_uk_notify_sms_queue'
    q = conn.create_queue(QueueName=name)
    return q
