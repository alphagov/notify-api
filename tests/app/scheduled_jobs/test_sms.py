import boto3
import moto
from flask import json
from mock import call
from app.models import Notification
from datetime import datetime
from app import db, sms_wrapper
from app.job.sms_jobs import send_sms, fetch_sms_status
from app.connectors.sms.clients import ClientException


@moto.mock_sqs
def test_should_send_sms_all_notifications(notify_api, notify_db, notify_db_session, notify_config, mocker):
    mocker.patch('app.sms_wrapper.send', return_value=("1234", "twilio"))
    create_notification = Notification(
        id=1000,
        to="to",
        message="message",
        created_at=datetime.utcnow(),
        status='created',
        method='sms',
        job_id=1234
    )
    db.session.add(create_notification)
    db.session.commit()

    read_notification_2 = Notification.query.get(1234)

    q = set_up_mock_queue()
    send_message_to_mock_queue(q, create_notification)
    send_message_to_mock_queue(q, read_notification_2)

    send_sms()

    # new one
    read_notification_1 = Notification.query.get(1000)
    assert read_notification_1.status == 'sent'
    assert read_notification_1.sent_at >= read_notification_1.created_at
    assert read_notification_1.sender_id == "1234"
    assert read_notification_1.sender == "twilio"

    # normal test session one
    read_notification_2 = Notification.query.get(1234)
    assert read_notification_2.status == 'sent'
    assert read_notification_2.sent_at >= read_notification_2.created_at
    assert read_notification_2.sender_id == "1234"
    assert read_notification_2.sender == "twilio"

    # sms calls made correctly
    sms_wrapper.send.assert_has_calls([call('phone-number', 'this is a message', 1234), call("to", "message", 1000)],
                                      any_order=True)


@moto.mock_sqs
def test_should_send_sms_notification(notify_api, notify_db, notify_db_session, notify_config, mocker):
    mocker.patch('app.sms_wrapper.send', return_value=("1234", "twilio"))
    q = set_up_mock_queue()
    send_message_to_mock_queue(q, Notification.query.get(1234))

    send_sms()

    read_notification = Notification.query.get(1234)
    assert read_notification.status == 'sent'
    assert read_notification.sender_id == "1234"
    assert read_notification.sender == "twilio"
    assert read_notification.sent_at >= read_notification.created_at
    sms_wrapper.send.assert_called_once_with('phone-number', 'this is a message', 1234)


@moto.mock_sqs
def test_only_send_notifications_in_created_state(notify_api, notify_db, notify_db_session, notify_config, mocker):
    mocker.patch('app.sms_wrapper.send', return_value=("1234", "twilio"))
    sent_at = datetime.utcnow()
    create_notification = Notification(
        id=1000,
        to="to",
        message="message",
        created_at=datetime.utcnow(),
        sent_at=sent_at,
        status='sent',
        sender='twilio',
        method='sms',
        job_id=1234,
        sender_id="999"
    )
    db.session.add(create_notification)
    db.session.commit()

    q = set_up_mock_queue()
    send_message_to_mock_queue(q, Notification.query.get(1234))

    send_sms()

    # new one
    read_notification_1 = Notification.query.get(1000)
    print(read_notification_1.sender)
    assert read_notification_1.status == 'sent'
    assert read_notification_1.sender_id == '999'
    assert read_notification_1.sender == 'twilio'
    assert read_notification_1.sent_at == sent_at

    # normal test session one
    read_notification_2 = Notification.query.get(1234)
    assert read_notification_2.status == 'sent'
    assert read_notification_2.sender_id == '1234'
    assert read_notification_2.sender == 'twilio'
    assert read_notification_2.sent_at >= read_notification_2.created_at

    # sms calls made correctly
    sms_wrapper.send.assert_called_once_with('phone-number', 'this is a message', 1234)


@moto.mock_sqs
def test_should_put_notification_into_error_if_failed(notify_api, notify_db, notify_db_session, notify_config, mocker):
    mocker.patch('app.sms_wrapper.send', side_effect=ClientException('twilio'))
    q = set_up_mock_queue()
    send_message_to_mock_queue(q, Notification.query.get(1234))
    send_sms()
    read_notification = Notification.query.get(1234)
    assert read_notification.status == 'error'
    assert read_notification.sender == 'twilio'
    assert read_notification.sent_at is None

    # sms calls made correctly
    sms_wrapper.send.assert_called_once_with('phone-number', 'this is a message', 1234)


def test_should_set_status_for_all_send_notifications(notify_api, notify_db, notify_db_session, notify_config, mocker):
    mocker.patch('app.sms_wrapper.status', return_value="delivered")

    sent_at = datetime.utcnow()
    create_notification = Notification(
        id=1000,
        to="to",
        message="message",
        created_at=datetime.utcnow(),
        sent_at=sent_at,
        status='sent',
        method='sms',
        job_id=1234,
        sender_id="1",
        sender="twilio"
    )
    db.session.add(create_notification)

    notification = Notification.query.get(1234)
    notification.status = 'sent'
    notification.sender_id = '2'
    notification.sender = 'twilio'
    db.session.add(notification)
    db.session.commit()

    fetch_sms_status()
    read_notification = Notification.query.get(1234)
    assert read_notification.status == 'delivered'
    assert read_notification.delivered_at >= read_notification.created_at
    sms_wrapper.status.assert_has_calls([call("1", "twilio"), call("2", "twilio")])


def test_should_set_status_for_send_notifications(notify_api, notify_db, notify_db_session, notify_config, mocker):
    mocker.patch('app.sms_wrapper.status', return_value="delivered")
    notification = Notification.query.get(1234)
    notification.status = 'sent'
    notification.sender_id = '1234'
    notification.sender = 'twilio'
    db.session.add(notification)
    db.session.commit()

    fetch_sms_status()
    read_notification = Notification.query.get(1234)
    assert read_notification.status == 'delivered'
    assert read_notification.delivered_at >= read_notification.created_at
    sms_wrapper.status.assert_called_once_with("1234", 'twilio')


def test_should_not_set_delivered_at_if_not_delivered(notify_api, notify_db, notify_db_session, notify_config, mocker):
    mocker.patch('app.sms_wrapper.status', return_value="failed")
    notification = Notification.query.get(1234)
    notification.status = 'sent'
    notification.sender_id = '1234'
    notification.sender = 'twilio'
    db.session.add(notification)
    db.session.commit()

    fetch_sms_status()
    read_notification = Notification.query.get(1234)
    assert read_notification.status == 'failed'
    assert not read_notification.delivered_at
    sms_wrapper.status.assert_called_once_with("1234", 'twilio')


def test_should_not_check_status_unless_sent(notify_api, notify_db, notify_db_session, notify_config, mocker):
    mocker.patch('app.sms_wrapper.status')

    fetch_sms_status()
    read_notification = Notification.query.get(1234)
    assert read_notification.status == 'created'
    assert not read_notification.delivered_at
    sms_wrapper.status.assert_not_called


def set_up_mock_queue():
    # set up mock queue
    boto3.setup_default_session(region_name='eu-west-1')
    conn = boto3.resource('sqs')
    q = conn.create_queue(QueueName='gov_uk_notify_sms_queue')
    return q


def send_message_to_mock_queue(queue, notification):
    queue.send_message(MessageBody=json.dumps(notification.serialize()),
                       MessageAttributes={'type': {'StringValue': 'sms', 'DataType': 'String'}})
