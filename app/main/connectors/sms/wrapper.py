from twilio.rest import TwilioRestClient

import os


class TwilioClient:

    def __init__(self):
        print(os.environ.get('TWILIO_ACCOUNT_SID'))
        print(os.environ.get('TWILIO_AUTH_TOKEN'))
        print(os.environ.get('TWILIO_NUMBER'))
        self.client = TwilioRestClient(
            os.environ.get('TWILIO_ACCOUNT_SID'),
            os.environ.get('TWILIO_AUTH_TOKEN')
        )
        self.twilio_number = os.environ.get('TWILIO_NUMBER')

    def send_message(self, to, message):
        self.client.messages.create(
            body=message,
            to=to,
            from_=self.twilio_number
        )