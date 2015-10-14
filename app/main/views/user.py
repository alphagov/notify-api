from datetime import datetime
from flask import jsonify, abort, request, current_app
from .. import main
from app import db
from app.main import encryption
from app.main.validators import valid_user_authentication_submission
from app.main.views import get_json_from_request
from app.models import User


@main.route('/users', methods=['GET'])
def fetch_user():
    email_address = request.args.get('email_address')
    if email_address:
        user = User.query.filter(
            User.email_address == email_address.lower()
        ).first()

        if not user:
            abort(404, "No user with email_address '{}'".format(email_address))

        return jsonify(
            users=user.serialize()
        ), 200
    else:
        abort(400, "No email address provided")


@main.route('/users/auth', methods=['POST'])
def auth_user():
    user_authentication_request = get_json_from_request('userAuthentication')

    validation_result, validation_errors = valid_user_authentication_submission(user_authentication_request)
    if not validation_result:
        return jsonify(
            error="Invalid JSON",
            error_details=validation_errors
        ), 400

    user = User.query.filter(
        User.email_address == user_authentication_request['emailAddress'].lower()
    ).first()

    if user is None:
        return jsonify(authorization=False), 404
    elif valid_user_auth(user_authentication_request['password'], user):
        user.logged_in_at = datetime.utcnow()
        user.failed_login_count = 0
        db.session.add(user)
        db.session.commit()

        return jsonify(users=user.serialize()), 200
    else:
        user.failed_login_count += 1
        db.session.add(user)
        db.session.commit()

        return jsonify(authorization=False), 403


def valid_user_auth(password_from_request, user):
    password_is_valid = encryption.checkpw(password_from_request, user.password)
    too_many_failed_logins = user.failed_login_count > current_app.config['MAX_FAILED_LOGIN_COUNT']

    if password_is_valid and user.active and not too_many_failed_logins:
        return True
    return False
