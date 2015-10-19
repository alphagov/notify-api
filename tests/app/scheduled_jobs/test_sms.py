from mock import call
from app.models import Notification
from datetime import datetime
from app import db, sms_wrapper
from app.job.sms_jobs import send_sms
from twilio import TwilioRestException


def test_should_send_sms_all_notifications(notify_api, notify_db, notify_db_session, notify_config, mocker):
    mocker.patch('app.sms_wrapper.send')
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

    send_sms()

    # new one
    read_notification_1 = Notification.query.get(1000)
    assert read_notification_1.status == 'sent'
    assert read_notification_1.sent_at >= read_notification_1.created_at

    # normal test session one
    read_notification_2 = Notification.query.get(1234)
    assert read_notification_2.status == 'sent'
    assert read_notification_2.sent_at >= read_notification_2.created_at

    # sms calls made correctly
    sms_wrapper.send.assert_has_calls([call('phone-number', 'this is a message', 1234), call("to", "message", 1000)])


def test_should_send_sms_notification(notify_api, notify_db, notify_db_session, notify_config, mocker):
    mocker.patch('app.sms_wrapper.send')
    send_sms()

    read_notification = Notification.query.get(1234)
    assert read_notification.status == 'sent'
    assert read_notification.sent_at >= read_notification.created_at
    sms_wrapper.send.assert_called_once_with('phone-number', 'this is a message', 1234)


def test_only_send_notifications_in_created_state(notify_api, notify_db, notify_db_session, notify_config, mocker):
    mocker.patch('app.sms_wrapper.send')
    sent_at = datetime.utcnow()
    create_notification = Notification(
        id=1000,
        to="to",
        message="message",
        created_at=datetime.utcnow(),
        sent_at=sent_at,
        status='sent',
        method='sms',
        job_id=1234
    )
    db.session.add(create_notification)
    db.session.commit()

    send_sms()

    # new one
    read_notification_1 = Notification.query.get(1000)
    assert read_notification_1.status == 'sent'
    assert read_notification_1.sent_at == sent_at

    # normal test session one
    read_notification_2 = Notification.query.get(1234)
    assert read_notification_2.status == 'sent'
    assert read_notification_2.sent_at >= read_notification_2.created_at

    # sms calls made correctly
    sms_wrapper.send.assert_called_once_with('phone-number', 'this is a message', 1234)


def test_should_put_notification_into_error_if_failed(notify_api, notify_db, notify_db_session, notify_config, mocker):
    mocker.patch('app.sms_wrapper.send', side_effect=TwilioRestException(503, "uri", "Failed"))
    send_sms()
    read_notification = Notification.query.get(1234)
    assert read_notification.status == 'error'
    assert read_notification.sent_at is None

    # sms calls made correctly
    sms_wrapper.send.assert_called_once_with('phone-number', 'this is a message', 1234)
