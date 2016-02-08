import os

from datetime import datetime

from flask import json

from app.models import Notification
from app import db, email_wrapper, create_app
from sqlalchemy import asc
from app.connectors.sms.clients import ClientException
from app.connectors.access_queue import get_messages_from_queue


def send_email():
    application = create_app(os.getenv('NOTIFY_API_ENVIRONMENT') or 'development')
    with application.app_context():
        try:
            notifications = get_messages_from_queue('email')
            for notification in notifications:
                print("Processing Email messages")
                print("notification: {}".format(notification.body))
                if notification.message_attributes.get('type').get('StringValue') == 'email':
                    try:
                        notification_body = json.loads(notification.body)
                        (message_id, sender) = email_wrapper.send(notification_body['to'],
                                                                  notification_body['sender'],
                                                                  'Notify Alpha',
                                                                  notification_body['message'],
                                                                  notification_body['id'])
                        notification.delete()
                        __update_notification_to_sent(message_id, notification_body, sender)
                        print("notification updated: {}".format(notification_body['id']))
                    except ClientException as e:
                        print(e)
                        __update_notification_to_error(notification_body['id'], e)

        except Exception as e:
            print(e)


def fetch_email_status():
    application = create_app(os.getenv('NOTIFY_API_ENVIRONMENT') or 'development')
    with application.app_context():
        notifications = Notification.query \
            .filter(Notification.status == 'sent') \
            .order_by(asc(Notification.sent_at)).all()
        for notification in notifications:
            print("Processing Email status")
            try:
                response_status = email_wrapper.status(notification.sender_id, notification.sender)
                if response_status:
                    notification.status = response_status
                    if response_status == 'delivered':
                        notification.delivered_at = datetime.utcnow()
                    db.session.add(notification)
                    db.session.commit()
            except ClientException as e:
                print(e)


def __update_notification_to_error(id, e):
    notification_to_update = Notification.query \
        .filter_by(id=id).first()
    notification_to_update.status = 'error'
    notification_to_update.sender = e.sender
    __update_notification(notification_to_update)


def __update_notification_to_sent(message_id, notification_body, sender):
    notification_to_update = Notification.query \
        .filter_by(id=notification_body['id']).first()
    notification_to_update.status = 'sent'
    notification_to_update.sent_at = datetime.utcnow()
    notification_to_update.sender_id = message_id
    notification_to_update.sender = sender
    __update_notification(notification_to_update)


def __update_notification(notification_to_update):
    db.session.add(notification_to_update)
    db.session.commit()
