from datetime import datetime
from flask import jsonify, abort, request, current_app
from .. import main
from app import db
from app.main.encryption import hashpw, checkpw
from app.main.validators import valid_user_authentication_submission, valid_create_user_submission, valid_email_address
from app.main.views import get_json_from_request
from app.models import User, Service
from sqlalchemy.exc import IntegrityError
from app.main.auth.token_auth import token_type_required


def check_user_and_service(service_id, email_address):
    service = Service.query.get(service_id)
    if not service:
        abort(404, 'Service not found')

    user = User.query.filter(
        User.email_address == email_address.lower()
    ).first()

    if not user:
        abort(404, "No user with given email address")

    return user, service


@main.route('/service/<int:service_id>/remove-user', methods=['POST'])
@token_type_required('admin')
def remove_user_from_service(service_id):
    json_request = get_json_from_request('user')

    validation_result, validation_errors = valid_email_address(json_request)
    if not validation_result:
        return jsonify(
            error="Invalid JSON",
            error_details=validation_errors
        ), 400

    user, service = check_user_and_service(service_id, json_request['emailAddress'])

    try:
        service.users.remove(user)
        db.session.add(service)
        db.session.commit()
        return jsonify(
            users=service.serialize()
        ), 200
    except IntegrityError as e:
        print(e.orig)
        db.session.rollback()
        abort(400, "failed to remove user from service")


@main.route('/service/<int:service_id>/add-user', methods=['POST'])
@token_type_required('admin')
def add_user_to_service(service_id):
    json_request = get_json_from_request('user')

    validation_result, validation_errors = valid_email_address(json_request)
    if not validation_result:
        return jsonify(
            error="Invalid JSON",
            error_details=validation_errors
        ), 400

    user, service = check_user_and_service(service_id, json_request['emailAddress'])

    service.users.append(user)
    try:
        db.session.add(service)
        db.session.commit()
        return jsonify(
            users=service.serialize()
        ), 200
    except IntegrityError as e:
        print(e.orig)
        db.session.rollback()
        abort(400, "failed to add user to service")


@main.route('/users/<int:user_id>', methods=['GET'])
@token_type_required('admin')
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
@token_type_required('admin')
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
@token_type_required('admin')
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


@main.route('/user/<int:user_id>/activate', methods=['POST'])
@token_type_required('admin')
def activate_user(user_id):
    user = User.query.get(user_id)

    if user is None:
        return jsonify(authorization=False), 404
    else:
        user.logged_in_at = datetime.utcnow()
        user.failed_login_count = 0
        user.active = True
        try:
            db.session.add(user)
            db.session.commit()
            return jsonify(users=user.serialize()), 200
        except IntegrityError as e:
            print(e.orig)
            db.session.rollback()
            abort(400, "failed to activate user")


@main.route('/users/auth', methods=['POST'])
@token_type_required('admin')
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
