import boto3
import moto
from flask import json

from app.models import Notification
from app import email_wrapper
from app.job.email_jobs import send_email, fetch_email_status


@moto.mock_sqs
def test_should_send_email_notification(notify_api, notify_db, notify_email_db_session, notify_config, mocker):
    mocker.patch('app.email_wrapper.send', return_value=("1234", "sendgrid"))
    set_up_mock_queue()
    send_email()

    read_notification = Notification.query.get(1234)
    assert read_notification.status == 'sent'
    assert read_notification.sender_id == "1234"
    assert read_notification.sender == "sendgrid"
    assert read_notification.sent_at >= read_notification.created_at
    email_wrapper.send.assert_called_once_with('test@test.com', None, 'subject placeholder', 'this is an email message',
                                               1234)


def test_should_not_check_status_unless_sent(notify_api, notify_db, notify_db_session, notify_config, mocker):
    mocker.patch('app.email_wrapper.status')

    fetch_email_status()
    read_notification = Notification.query.get(1234)
    assert read_notification.status == 'created'
    assert not read_notification.delivered_at
    email_wrapper.status.assert_not_called



def set_up_mock_queue():
    # set up mock queue
    boto3.setup_default_session(region_name='eu-west-1')
    conn = boto3.resource('sqs')
    q = conn.create_queue(QueueName='gov_uk_notify_queue')
    data = json.dumps({
        "notification": {
            "to": "customer@test.com",
            "from": "service@example.gov.uk",
            "subject": "Email subject",
            "message": "This is an email message"
        }
    })
    q.send_message(MessageBody=data,
                   MessageAttributes={'type': {'StringValue': 'email', 'DataType': 'String'}})
    return q