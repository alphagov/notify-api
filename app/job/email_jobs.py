import os

from datetime import datetime
from app.models import Notification
from app import db, email_wrapper, create_app
from sqlalchemy import asc
from app.connectors.sms.clients import ClientException


def send_email():
    print("Processing Email messages")
    application = create_app(os.getenv('NOTIFY_API_ENVIRONMENT') or 'development')
    with application.app_context():
        try:
            notifications = Notification.query\
                .filter(Notification.status == 'created') \
                .filter(Notification.method == 'email')\
                .order_by(asc(Notification.created_at)).all()

            for notification in notifications:
                try:
                    # sendMessagesToQueue('email', json.dumps(notification.serialize()))

                    (message_id, sender) = email_wrapper.send(notification.to,
                                                              notification.sender,
                                                              "subject placeholder",
                                                              notification.message, notification.id)
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
        except Exception as e:
            print(e)


def fetch_email_status():
    print("Processing Email status")
    application = create_app(os.getenv('NOTIFY_API_ENVIRONMENT') or 'development')
    with application.app_context():
        notifications = Notification.query \
            .filter(Notification.status == 'sent') \
            .order_by(asc(Notification.sent_at)).all()
        for notification in notifications:
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
