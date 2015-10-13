from twilio.rest import TwilioRestClient

import os


class SmsClient:

    def __setup(self):
        pass

    def send(self, to, message, message_id):
        pass

    def log(self, message_id):
        pass


class TwilioClient(SmsClient):

    def __init__(self, app):
        (twilio_account_sid, twilio_auth_token, twilio_number) = self.__setup(app)
        self.client = TwilioRestClient(twilio_account_sid, twilio_auth_token)
        self.twilio_number = twilio_number

    def __setup(self, app):
        twilio_account_sid = app.config.get('TWILIO_ACCOUNT_SID')
        twilio_auth_token = app.config.get('TWILIO_AUTH_TOKEN')
        twilio_number = app.config.get('TWILIO_NUMBER')

        if not all([twilio_account_sid, twilio_auth_token, twilio_number]):
            raise RuntimeError("Twilio incorrectly configured")

        return twilio_account_sid, twilio_auth_token, twilio_number

    def send(self, to, message, message_id):
        self.client.messages.create(
            body=message,
            to=to,
            from_=self.twilio_number
        )
        self.log(message_id)

    def log(self, message_id):
        print("Twilio has sent {}".format(message_id))
