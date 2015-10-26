from datetime import datetime
from flask import jsonify, abort, request, current_app
from .. import main
from app import db
from app.main.encryption import hashpw, checkpw
from app.main.validators import valid_user_authentication_submission, valid_create_user_submission
from app.main.views import get_json_from_request
from app.models import User
from sqlalchemy.exc import IntegrityError


@main.route('/users/<int:user_id>', methods=['GET'])
def fetch_user_by_id(user_id):
    user = User.query.filter(
        User.id == user_id
    ).first()

    if not user:
        abort(404, "No user with id '{}'".format(user_id))

    return jsonify(
        users=user.serialize()
    ), 200


@main.route('/users', methods=['GET'])
def fetch_user_by_email():
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


@main.route('/users', methods=['POST'])
def create_user():
    user_creation_request = get_json_from_request('user')
    validation_result, validation_errors = valid_create_user_submission(user_creation_request)
    if not validation_result:
        return jsonify(
            error="Invalid JSON",
            error_details=validation_errors
        ), 400

    user = User(
        email_address=user_creation_request['emailAddress'].lower(),
        mobile_number=user_creation_request['mobileNumber'],
        password=hashpw(user_creation_request['password']),
        active=False,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
        logged_in_at=datetime.utcnow(),
        password_changed_at=datetime.utcnow(),
        failed_login_count=0,
        role='admin'
    )

    try:
        db.session.add(user)
        db.session.commit()
        return jsonify(
            users=user.serialize()
        ), 201
    except IntegrityError as e:
        print(e.orig)
        db.session.rollback()
        abort(400, "failed to create user")


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
    password_is_valid = checkpw(password_from_request, user.password)
    too_many_failed_logins = user.failed_login_count > current_app.config['MAX_FAILED_LOGIN_COUNT']

    if password_is_valid and user.active and not too_many_failed_logins:
        return True
    return False
