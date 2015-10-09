from . import db

DATETIME_FORMAT = "%Y-%m-%dT%H:%M:%S.%fZ"


class Organisation(db.Model):
    __tablename__ = 'organisation'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)

    def serialize(self):
        serialized = {
            'id': self.id,
            'name': self.name
        }

        return filter_null_value_fields(serialized)


class Service(db.Model):
    __tablename__ = 'service'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    token = db.Column(db.String(255), nullable=False)
    organisation_id = db.Column(db.BigInteger, db.ForeignKey('organisation.id'), index=True, unique=False)
    organisation = db.relationship(Organisation, lazy='joined', innerjoin=True)
    created_at = db.Column(db.DateTime, index=False, unique=False, nullable=False)

    def serialize(self):
        serialized = {
            'id': self.id,
            'name': self.name,
            'organisation': self.organisation.serialize(),
            'createdAt': self.created_at.strftime(DATETIME_FORMAT)
        }

        return filter_null_value_fields(serialized)


class Job(db.Model):
    __tablename__ = 'job'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    service_id = db.Column(db.BigInteger, db.ForeignKey('service.id'), index=True, unique=False)
    service = db.relationship(Service, lazy='joined', innerjoin=True)
    created_at = db.Column(db.DateTime, index=False, unique=False, nullable=False)

    def serialize(self):
        serialized = {
            'id': self.id,
            'name': self.name,
            'service': self.service.serialize(),
            'createdAt': self.created_at.strftime(DATETIME_FORMAT)
        }

        return filter_null_value_fields(serialized)


class Notification(db.Model):
    __tablename__ = 'notification'

    id = db.Column(db.Integer, primary_key=True)
    job_id = db.Column(db.BigInteger, db.ForeignKey('job.id'), index=True, unique=False)
    job = db.relationship(Job, lazy='joined', innerjoin=True)
    to = db.Column(db.String(255), nullable=False)
    message = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, index=False, unique=False, nullable=False)
    delivered_at = db.Column(db.DateTime, index=False, unique=False, nullable=True)
    status = db.Column(db.String(255), nullable=False)
    type = db.Column(db.String(255), nullable=False)

    def serialize(self):
        serialized = {
            'id': self.id,
            'job': self.job.serialize(),
            'message': self.message,
            'createdAt': self.created_at.strftime(DATETIME_FORMAT),
            'deliveredAt': self.delivered_at.strftime(DATETIME_FORMAT),
            'status': self.status,
            'type': self.type
        }

        return filter_null_value_fields(serialized)


class User(db.Model):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    email_address = db.Column(db.String(255), nullable=False, index=True)
    password = db.Column(db.String, index=False, unique=False, nullable=False)
    active = db.Column(db.Boolean, index=False, unique=False, nullable=False)
    locked = db.Column(db.Boolean, index=False, unique=False, nullable=False)
    created_at = db.Column(db.DateTime, index=False, unique=False, nullable=False)
    updated_at = db.Column(db.DateTime, index=False, unique=False, nullable=False)
    password_changed_at = db.Column(db.DateTime, index=False, unique=False, nullable=False)
    role = db.Column(db.String, index=False, unique=False, nullable=False)
    organisation_id = db.Column(db.Integer, db.ForeignKey('organisation.id'), index=True, unique=False, nullable=True)


def filter_null_value_fields(obj):
    return dict(
        filter(lambda x: x[1] is not None, obj.items())
    )
