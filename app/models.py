from . import db
from flask import current_app

DATETIME_FORMAT = "%Y-%m-%dT%H:%M:%S.%fZ"


class Notification(db.Model):
    __tablename__ = 'notifications'

    id = db.Column(db.Integer, primary_key=True)

    job_id = db.Column(db.BigInteger, db.ForeignKey('jobs.id'), index=True, unique=False)
    job = db.relationship('Job', backref=db.backref('notifications', lazy='dynamic'))

    to = db.Column(db.String(255), nullable=False)
    message = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, index=False, unique=False, nullable=False)
    sent_at = db.Column(db.DateTime, index=False, unique=False, nullable=True)
    delivered_at = db.Column(db.DateTime, index=False, unique=False, nullable=True)
    status = db.Column(db.String(255), nullable=False)
    method = db.Column(db.String(255), nullable=False)
    sender_id = db.Column(db.String(255), index=True, nullable=True)

    def serialize(self):
        serialized = {
            'id': self.id,
            'to': self.to,
            'message': self.message,
            'createdAt': none_or_formatted_date(self.created_at),
            'sentAt': none_or_formatted_date(self.sent_at),
            'deliveredAt': none_or_formatted_date(self.delivered_at),
            'status': self.status,
            'method': self.method,
            'jobId': self.job_id
        }

        return filter_null_value_fields(serialized)


class Job(db.Model):
    __tablename__ = 'jobs'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, index=False, unique=False, nullable=False)

    service_id = db.Column(db.BigInteger, db.ForeignKey('services.id'), index=True, unique=False)
    service = db.relationship('Service', backref=db.backref('jobs', lazy='dynamic'))

    def serialize(self):
        serialized = {
            'id': self.id,
            'name': self.name,
            'createdAt': self.created_at.strftime(DATETIME_FORMAT),
            'serviceId': self.service_id
        }

        return filter_null_value_fields(serialized)


user_to_service = db.Table(
    'user_to_service',
    db.Model.metadata,
    db.Column('user_id', db.Integer, db.ForeignKey('users.id')),
    db.Column('service_id', db.Integer, db.ForeignKey('services.id'))
)

class Service(db.Model):
    __tablename__ = 'services'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)

    token_id = db.Column(db.BigInteger, db.ForeignKey('token.id'), index=True, unique=True)
    token = db.relationship('Token', backref=db.backref('services', lazy='dynamic'))

    organisations_id = db.Column(db.Integer, db.ForeignKey('organisations.id'))
    organisation = db.relationship('Organisation', backref=db.backref('services', lazy='dynamic'))

    created_at = db.Column(db.DateTime, index=False, unique=False, nullable=False)

    active = db.Column(db.Boolean, index=False, unique=False, nullable=False)

    limit = db.Column(db.BigInteger, index=False, unique=False, nullable=False)

    users = db.relationship('User', secondary=user_to_service, backref='services')

    def serialize(self):
        serialized = {
            'id': self.id,
            'name': self.name,
            'createdAt': self.created_at.strftime(DATETIME_FORMAT),
            'active': self.active,
            'limit': self.limit,
            'organisationId': self.organisations_id,
            'token': self.token.serialize()
        }

        return filter_null_value_fields(serialized)


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email_address = db.Column(db.String(255), nullable=False, index=True)
    password = db.Column(db.String, index=False, unique=False, nullable=False)
    active = db.Column(db.Boolean, index=False, unique=False, nullable=False)
    created_at = db.Column(db.DateTime, index=False, unique=False, nullable=False)
    updated_at = db.Column(db.DateTime, index=False, unique=False, nullable=False)
    password_changed_at = db.Column(db.DateTime, index=False, unique=False, nullable=False)
    logged_in_at = db.Column(db.DateTime, nullable=True)
    failed_login_count = db.Column(db.Integer, nullable=False, default=0)
    role = db.Column(db.String, index=False, unique=False, nullable=False)
    organisation_id = db.Column(db.Integer, db.ForeignKey('organisations.id'), index=True, unique=False, nullable=True)
    organisation = db.relationship('Organisation', backref=db.backref('users', lazy='dynamic'))

    def serialize(self):
        serialized = {
            'id': self.id,
            'emailAddress': self.email_address,
            'active': self.active,
            'locked': self.failed_login_count > current_app.config['MAX_FAILED_LOGIN_COUNT'],
            'createdAt': self.created_at.strftime(DATETIME_FORMAT),
            'updatedAt': self.updated_at.strftime(DATETIME_FORMAT),
            'passwordChangedAt': self.password_changed_at.strftime(DATETIME_FORMAT),
            'role': self.role,
            'organisationId': self.organisation_id,
            'failedLoginCount': self.failed_login_count
        }

        return filter_null_value_fields(serialized)


class Organisation(db.Model):
    __tablename__ = 'organisations'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)

    def serialize(self):
        serialized = {
            'id': self.id,
            'name': self.name
        }

        return filter_null_value_fields(serialized)


class Token(db.Model):
    __tablename__ = "token"

    id = db.Column(db.Integer, primary_key=True)
    token = db.Column(db.String(255), nullable=False)

    def serialize(self):
        serialized = {
            'id': self.id,
            'token': self.token
        }

        return filter_null_value_fields(serialized)


def filter_null_value_fields(obj):
    return dict(
        filter(lambda x: x[1] is not None, obj.items())
    )


def none_or_formatted_date(date):
    if date:
        return date.strftime(DATETIME_FORMAT)
    else:
        return None
