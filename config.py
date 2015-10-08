
class Config(object):
    DEBUG = False
    NOTIFY_HTTP_PROTO = 'http'
    AUTH_REQUIRED = True
    API_TOKEN = '$2a$10$JGHuLQA..8GKdKlHoKxa6exqRy0/awKAj7E9TCbVXteADL/Xg5i8C'
    SMS_ENABLED = True


class Development(Config):
    DEBUG = True


class Test(Config):
    DEBUG = True


class Live(Config):
    NOTIFY_HTTP_PROTO = "https"


configs = {
    'development': Development,
    'test': Test,
    'live': Live,
}
