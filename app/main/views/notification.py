from uuid import uuid4
from flask import jsonify, current_app, request, abort
from app.main.validators import valid_sms_notification
from .. import main, get_token_from_headers
from ... import db
from ... import sms_wrapper
from sqlalchemy.exc import IntegrityError, DataError
from app.models import Service, Job, Notification
from datetime import datetime


@main.route('/notifications', methods=['GET'])
def fetch_notifications():
    incoming_token = get_token_from_headers(request.headers)
    service = Service.query.filter(Service.token == incoming_token).first_or_404()

    notifications = Notification.query.join(Job).filter(Job.service_id == service.id).all()

    return jsonify(
        notifications=[notification.serialize() for notification in notifications],
    )

@main.route('/sms/notification', methods=['POST'])
def create_sms_notification():
    if not current_app.config['SMS_ENABLED']:
        return jsonify(error="SMS is unavailable"), 503

    notification = get_json_from_request()

    validation_result, validation_errors = valid_sms_notification(notification)
    if not validation_result:
        return jsonify(
            error="Invalid JSON",
            error_details=validation_errors
        ), 400
    message_id = str(uuid4())
    sms_wrapper.send(notification['to'], notification['message'], message_id)

    return jsonify(
        id=message_id
    )

# @main.route('/sms/notification', methods=['POST'])
# def create_sms_notification():
#     if not current_app.config['SMS_ENABLED']:
#         return jsonify(error="SMS is unavailable"), 503
#
#     notification_request = get_json_from_request()
#
#     validation_result, validation_errors = valid_sms_notification(notification_request)
#
#     # if not validation_result:
#     #     return jsonify(
#     #         error="Invalid JSON",
#     #         error_details=validation_errors
#     #     ), 400
#     #
#     # incoming_token = get_token_from_headers(request.headers)
#     # service = Service.query.filter(Service.token == incoming_token).first_or_404()
#     #
#     # if "job_id" in notification_request:
#     #     job = Job.query.filter(Job.id == notification_request["job_id"]).first_or_404()
#     #     if job.service_id != service.id:
#     #         abort(400, "invalid job id")
#     #
#     # notification = Notification(
#     #     job_id=notification_request.get("job_id", None),
#     #     to=notification_request['to'],
#     #     message=notification_request['message'],
#     #     status='created',
#     #     type='sms',
#     #     created_at=datetime
#     # )
#
#     try:
#         # db.session.add(notification)
#         db.session.flush()
#
#         #sms_wrapper.send(notification.to, notification.message, "notification.id")
#
#         #db.session.commit()
#     except IntegrityError:
#         db.session.rollback()
#         abort(400, "Invalid job id")
#
#     return jsonify(
#         notification="notification.serialize()"
#     )
#

def get_json_from_request():
    if request.content_type not in [
        'application/json',
        'application/json; charset=UTF-8'
    ]:
        abort(400, "Unexpected Content-Type, expecting 'application/json'")
    data = request.get_json()
    if data is None:
        abort(400, "Invalid JSON; must be a valid JSON object")
    if 'notification' not in data:
        abort(400, "Invalid JSON; must have notification as root element")
    return data['notification']
