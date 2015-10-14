from . import db

DATETIME_FORMAT = "%Y-%m-%dT%H:%M:%S.%fZ"


class Notification(db.Model):
    __tablename__ = 'notifications'

    id = db.Column(db.Integer, primary_key=True)
    job_id = db.Column(db.BigInteger, db.ForeignKey('jobs.id'), index=True, unique=False)
    to = db.Column(db.String(255), nullable=False)
    message = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, index=False, unique=False, nullable=False)
    delivered_at = db.Column(db.DateTime, index=False, unique=False, nullable=True)
    status = db.Column(db.String(255), nullable=False)
    method = db.Column(db.String(255), nullable=False)

    def serialize(self):
        serialized = {
            'id': self.id,
            'message': self.message,
            'createdAt': self.created_at.strftime(DATETIME_FORMAT),
            'status': self.status,
            'method': self.method,
            'jobId': self.job_id
        }

        return filter_null_value_fields(serialized)


class Job(db.Model):
    __tablename__ = 'jobs'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    service_id = db.Column(db.BigInteger, db.ForeignKey('services.id'), index=True, unique=False)
    created_at = db.Column(db.DateTime, index=False, unique=False, nullable=False)
    notification = db.relationship(Notification, backref='notifications', lazy='joined', innerjoin=False)

    def serialize(self):
        serialized = {
            'id': self.id,
            'name': self.name,
            'createdAt': self.created_at.strftime(DATETIME_FORMAT)
        }

        return filter_null_value_fields(serialized)


class Service(db.Model):
    __tablename__ = 'services'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    token_id = db.Column(db.BigInteger, db.ForeignKey('token.id'), index=True, unique=True)

    job = db.relationship(Job, backref='services', lazy='joined', innerjoin=False)

    organisations_id = db.Column(db.Integer, db.ForeignKey('organisations.id'))

    created_at = db.Column(db.DateTime, index=False, unique=False, nullable=False)

    def serialize(self):
        serialized = {
            'id': self.id,
            'name': self.name,
            'createdAt': self.created_at.strftime(DATETIME_FORMAT)
        }

        return filter_null_value_fields(serialized)


class Organisation(db.Model):
    __tablename__ = 'organisations'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    service = db.relationship(Service, backref='services', lazy='joined', innerjoin=False)

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
    service = db.relationship(Service, backref='service', lazy='joined', innerjoin=False)


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email_address = db.Column(db.String(255), nullable=False, index=True)
    password = db.Column(db.String, index=False, unique=False, nullable=False)
    active = db.Column(db.Boolean, index=False, unique=False, nullable=False)
    locked = db.Column(db.Boolean, index=False, unique=False, nullable=False)
    created_at = db.Column(db.DateTime, index=False, unique=False, nullable=False)
    updated_at = db.Column(db.DateTime, index=False, unique=False, nullable=False)
    password_changed_at = db.Column(db.DateTime, index=False, unique=False, nullable=False)
    role = db.Column(db.String, index=False, unique=False, nullable=False)
    organisation_id = db.Column(db.Integer, db.ForeignKey('organisations.id'), index=True, unique=False, nullable=True)
    organisation = db.relationship(Organisation, lazy='joined', innerjoin=True)


def filter_null_value_fields(obj):
    return dict(
        filter(lambda x: x[1] is not None, obj.items())
    )
