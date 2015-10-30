from .sms.clients import TwilioClient, PlivoClient
import random


class SmsWrapper:

    def __init__(self, app=None):
        self.app = app
        if app is not None:
            self.init_app(app)

        self.__clients__ = {}

    def init_app(self, app):
        twilio = TwilioClient(app)
        plivo = PlivoClient(app)
        self.__clients__.update({twilio.identifier: twilio})
        self.__clients__.update({plivo.identifier: plivo})

    def send(self, to, message, message_id):
        """
        Picks a random client from the list and sends the sms through that provider

        :param to: mobile number to send to
        :param message: message
        :param message_id: unique notify id for this message
        :return: 3rd party message ID and sender identifier
        """
        client = self.__clients__[random.choice(list(self.__clients__.keys()))]
        return client.send(to, message, message_id)

    def status(self, message_id, identifier):
        """

        :param message_id: 3rd party sender id
        :param identifier: identifier of the 3rd party who sent the message
        :return:
        """
        return self.__clients__[identifier].status(message_id)
