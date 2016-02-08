import os

from datetime import datetime

from flask import json

from app.connectors.access_queue import get_messages_from_queue
from app.models import Notification
from app import db, sms_wrapper, create_app
from sqlalchemy import asc
from app.connectors.sms.clients import ClientException


def __update_notification_to_sent(id, message_id, sender):
    notification = Notification.query.filter_by(id=id).first()
    notification.status = 'sent'
    notification.sent_at = datetime.utcnow()
    notification.sender_id = message_id
    notification.sender = sender
    db.session.add(notification)
    db.session.commit()


def __update_notification_in_error(e, id, sender):
    notification = Notification.query.filter_by(id=id).first()
    notification.status = 'error'
    notification.sender = e.sender
    db.session.add(notification)
    db.session.commit()


def send_sms():
    application = create_app(os.getenv('NOTIFY_API_ENVIRONMENT') or 'development')
    with application.app_context():
        notifications = get_messages_from_queue('sms')
        for notification in notifications:
            if notification.message_attributes.get('type').get('StringValue') == 'sms':
                print("Processing SMS messages")
                try:
                    notification_body = json.loads(notification.body)
                    print("Processing {}".format(notification_body['id']))
                    print("notification: {}".format(notification.body))
                    (message_id, sender) = sms_wrapper.send(notification_body['to'],
                                                            notification_body['message'],
                                                            notification_body['id'])
                    notification.delete()
                    __update_notification_to_sent(notification_body['id'], message_id, sender)

                except ClientException as e:
                    print(e)
                    __update_notification_in_error(e, notification_body['id'], e.sender)


def fetch_sms_status():
    application = create_app(os.getenv('NOTIFY_API_ENVIRONMENT') or 'development')
    with application.app_context():
        notifications = Notification.query \
            .filter(Notification.status == 'sent') \
            .order_by(asc(Notification.sent_at)).all()
        for notification in notifications:
            print("Processing SMS status")
            try:
                response_status = sms_wrapper.status(notification.sender_id, notification.sender)
                if response_status:
                    notification.status = response_status
                    if response_status == 'delivered':
                        notification.delivered_at = datetime.utcnow()
                    db.session.add(notification)
                    db.session.commit()
            except ClientException as e:
                print(e)
