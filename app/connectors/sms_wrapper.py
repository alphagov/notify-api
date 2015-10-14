from .sms.clients import TwilioClient


class SmsWrapper:

    def __init__(self, app=None):
        self.app = app
        if app is not None:
            self.init_app(app)

        self.__clients__ = []

    def init_app(self, app):
        self.__clients__.append(TwilioClient(app))

    def send(self, to, message, message_id):
        self.__clients__[0].send(to, message, message_id)
