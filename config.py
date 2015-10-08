
class Config(object):
    DEBUG = False
    NOTIFY_HTTP_PROTO = 'http'
    AUTH_REQUIRED = True
    API_TOKEN = '$2a$10$JGHuLQA..8GKdKlHoKxa6exqRy0/awKAj7E9TCbVXteADL/Xg5i8C'
    SMS_ENABLED = True
    SQLALCHEMY_COMMIT_ON_TEARDOWN = False
    SQLALCHEMY_RECORD_QUERIES = True
    SQLALCHEMY_DATABASE_URI = 'postgresql://localhost/notify'


class Development(Config):
    DEBUG = True
    AUTH_REQUIRED = False


class Test(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'postgresql://localhost/notify_test'


class Live(Config):
    NOTIFY_HTTP_PROTO = "https"


configs = {
    'development': Development,
    'test': Test,
    'live': Live,
}
