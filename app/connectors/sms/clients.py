from twilio.rest import TwilioRestClient
import plivo
from twilio import TwilioRestException


class ClientException(Exception):
    def __init__(self, sender):
        self.sender = sender


class SmsClient:
    def __setup(self, app):
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
        self.identifier = 'twilio'

    def __setup(self, app):
        twilio_account_sid = app.config.get('TWILIO_ACCOUNT_SID')
        twilio_auth_token = app.config.get('TWILIO_AUTH_TOKEN')
        twilio_number = app.config.get('TWILIO_NUMBER')

        if not all([twilio_account_sid, twilio_auth_token, twilio_number]):
            raise RuntimeError("Twilio incorrectly configured")

        return twilio_account_sid, twilio_auth_token, twilio_number

    def send(self, to, message, message_id):
        try:
            response = self.client.messages.create(
                body=message,
                to=to,
                from_=self.twilio_number
            )
            self.log(message_id)
            return response.sid, self.identifier
        except TwilioRestException as e:
            print(e)
            raise ClientException(self.identifier)

    def status(self, message_id):
        try:
            response = self.client.messages.get(message_id)
            if response.status in ('delivered', 'undelivered', 'failed'):
                return response.status
            else:
                print("Message {} status {}".format(message_id, response.status))
                return None
        except TwilioRestException as e:
            print(e)
            raise ClientException(self.identifier)

    def log(self, message_id):
        print("Twilio has sent {}".format(message_id))


class PlivoClient(SmsClient):

    identifier = 'plivo'

    def __init__(self, app):
        (account_sid, auth_token, number) = self.__setup(app)
        self.client = plivo.RestAPI(account_sid, auth_token)

    def __setup(self, app):
        account_sid = app.config.get('PLIVO_ACCOUNT_SID')
        auth_token = app.config.get('PLIVO_AUTH_TOKEN')
        number = app.config.get('TWILIO_NUMBER')

        if not all([account_sid, auth_token, number]):
            raise RuntimeError("Plivo incorrectly configured")

        return account_sid, auth_token, number

    def send(self, to, message, message_id):
        params = {
            'src': self.number,
            'dst': to,
            'text': message,
            'type': "sms",
        }

        response = self.client.send_message(params)
        self.log(message_id)
        return response

    def status(self, message_id):
        response = self.client.get_message(message_id)
        if response.status in ('delivered', 'undelivered', 'failed'):
            return response.status
        else:
            print("Message {} status {}".format(message_id, response.status))
            return None

    def log(self, message_id):
        print("Plivo has sent {}".format(message_id))
