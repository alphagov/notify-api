from .sms.clients import SendGridClient
import random


class EmailWrapper:
    def __init__(self, app=None):
        self.app = app
        if app is not None:
            self.init_app(app)

        self.__clients__ = {}

    def init_app(self, app):
        send_grid = SendGridClient(app)

        self.__clients__.update({send_grid.identifier: send_grid})

    def send(self, to, sender, subject, body, message_id):
        """
        Picks a random client from the list and sends the email through that provider

        :param to: email address to send to
        :param sender: sender email address
        :param subject: email subject
        :param body: email body
        :param message_id: unique notify id for this message
        :return: 3rd party message ID and sender identifier
        """
        client = self.__clients__[random.choice(list(self.__clients__.keys()))]
        return client.send(to, sender, subject, body, message_id)

    def status(self, message_id, identifier):
        """

        :param message_id: 3rd party sender id
        :param identifier: identifier of the 3rd party who sent the message
        :return:
        """
        return self.__clients__[identifier].status(message_id)
