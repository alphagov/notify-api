import os

from datetime import datetime
from app.models import Notification
from app import db, sms_wrapper, create_app
from sqlalchemy import asc
from twilio import TwilioRestException


def send_sms():
    application = create_app(os.getenv('NOTIFY_API_ENVIRONMENT') or 'development')
    with application.app_context():
        notifications = Notification.query\
            .filter(Notification.status == 'created')\
            .order_by(asc(Notification.created_at)).all()
        for notification in notifications:
            try:
                sms_wrapper.send(notification.to, notification.message, notification.id)
                notification.status = 'sent'
                notification.sent_at = datetime.utcnow()
                db.session.add(notification)
                db.session.commit()
            except TwilioRestException as e:
                print(e)
                notification.status = 'error'
                db.session.add(notification)
                db.session.commit()
