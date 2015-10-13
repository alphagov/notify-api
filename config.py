
class Config(object):
    DEBUG = False
    NOTIFY_HTTP_PROTO = 'http'
    AUTH_REQUIRED = True
    API_TOKEN = '$2a$10$JGHuLQA..8GKdKlHoKxa6exqRy0/awKAj7E9TCbVXteADL/Xg5i8C'
    SMS_ENABLED = True
    SQLALCHEMY_COMMIT_ON_TEARDOWN = False
    SQLALCHEMY_RECORD_QUERIES = True
    SQLALCHEMY_DATABASE_URI = 'postgresql://localhost/notify'

    # Clients
    TWILIO_ACCOUNT_SID = 'ACCOUNT_ID'
    TWILIO_AUTH_TOKEN = 'AUTH_TOKEN'
    TWILIO_NUMBER = '1234'


class Development(Config):
    DEBUG = True
    AUTH_REQUIRED = False


class Test(Config):
    DEBUG = True
    API_TOKEN = '$2a$10$egbx39iRQppzxwquEmYUDeM.S0qHnfuRP9JqZuwXAk6XCFGs/V3We'
    AUTH_REQUIRED = False
    SQLALCHEMY_DATABASE_URI = 'postgresql://localhost/notify_test'


class Live(Config):
    NOTIFY_HTTP_PROTO = "https"


configs = {
    'development': Development,
    'test': Test,
    'live': Live,
}
