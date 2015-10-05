
class Config:
    DEBUG = False


class Development(Config):
    DEBUG = True


class Test(Config):
    DEBUG = True


class Live(Config):
    """Base config for deployed environments"""
    pass

configs = {
    'development': Development,
    'test': Test,
    'live': Live,
}
