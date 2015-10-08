from flask import jsonify, url_for, current_app, request, abort
from app.main.validators import valid_sms_notification
from .. import main
from ... import sms_wrapper
from uuid import uuid4


@main.route('/')
def index():
    """Entry point for the API, show the resources that are available."""
    return jsonify(links={
        "notification.create": {
            "url": url_for(
                '.create_sms_notification',
                _external=True,
                _scheme=current_app.config.get('NOTIFY_HTTP_PROTO', 'http')
            ),
            "method": "POST"
        }
    }
    ), 200


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
