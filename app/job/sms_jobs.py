import os

from datetime import datetime
from app.models import Notification
from app import db, sms_wrapper, create_app
from sqlalchemy import asc
from app.connectors.sms.clients import ClientException


def send_sms():
    print("Processing SMS messages")
    application = create_app(os.getenv('NOTIFY_API_ENVIRONMENT') or 'development')
    with application.app_context():
        notifications = Notification.query\
            .filter(Notification.status == 'created')\
            .order_by(asc(Notification.created_at)).all()
        for notification in notifications:
            print("Processing {}".format(notification.id))
            try:
                (message_id, sender) = sms_wrapper.send(notification.to, notification.message, notification.id)
                notification.status = 'sent'
                notification.sent_at = datetime.utcnow()
                notification.sender_id = message_id
                notification.sender = sender
                db.session.add(notification)
                db.session.commit()
            except ClientException as e:
                print(e)
                notification.status = 'error'
                notification.sender = e.sender
                db.session.add(notification)
                db.session.commit()


def fetch_sms_status():
    print("Processing SMS status")
    application = create_app(os.getenv('NOTIFY_API_ENVIRONMENT') or 'development')
    with application.app_context():
        notifications = Notification.query\
            .filter(Notification.status == 'sent')\
            .order_by(asc(Notification.sent_at)).all()
        for notification in notifications:
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
