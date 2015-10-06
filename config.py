
class Config(object):
    DEBUG = False
    NOTIFY_HTTP_PROTO = 'http'
    AUTH_REQUIRED = True
    API_TOKEN = 'valid-token'


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
