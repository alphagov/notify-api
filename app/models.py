from . import db


class Organisation(db.Model):
    __tablename__ = 'organisation'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)


class Service(db.Model):
    __tablename__ = 'service'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    organisation_id = db.Column(db.Integer, db.ForeignKey('organisation.id'))
    created_at = db.Column(db.DateTime, index=False, unique=False, nullable=False)


class Job(db.Model):
    __tablename__ = 'job'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    service_id = db.Column(db.Integer, db.ForeignKey('service.id'))
    created_at = db.Column(db.DateTime, index=False, unique=False, nullable=False)


class Notification(db.Model):
    __tablename__ = 'message'

    id = db.Column(db.Integer, primary_key=True)
    job_id = db.Column(db.Integer, db.ForeignKey('job.id'))
    to = db.Column(db.String(255), nullable=False)
    message = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, index=False, unique=False, nullable=False)
    delivered_at = db.Column(db.DateTime, index=False, unique=False, nullable=True)
    status = db.Column(db.String(255), nullable=False)
    type = db.Column(db.String(255), nullable=False)

0
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