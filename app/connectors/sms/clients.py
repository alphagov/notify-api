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
        twilio_number = app.config.get('FROM_NUMBER')

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

    def __init__(self, app):
        (account_sid, auth_token, number) = self.__setup(app)
        self.client = plivo.RestAPI(account_sid, auth_token)
        self.number = number
        self.identifier = 'plivo'

    def __setup(self, app):
        account_sid = app.config.get('PLIVO_ACCOUNT_SID')
        auth_token = app.config.get('PLIVO_AUTH_TOKEN')
        number = app.config.get('FROM_NUMBER')

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

        try:
            # Sample successful output
            # (202,
            #       {
            #               u'message': u'message(s) queued',
            #               u'message_uuid': [u'b795906a-8a79-11e4-9bd8-22000afa12b9'],
            #               u'api_id': u'b77af520-8a79-11e4-b153-22000abcaa64'
            #       }
            # )
            response = self.client.send_message(params)
            self.log(message_id)
            return response[1]['message_uuid'][0], self.identifier
        except TwilioRestException as e:
            print(e)
            raise ClientException(self.identifier)

    def status(self, message_id):
        try:
            params = {
                'message_uuid': message_id
            }
            # Sample response
            # (200,
            #     {
            #        u'message_state': u'delivered',
            #        u'total_amount': u'0.02600',
            #        u'to_number': u'3333333333',
            #        u'total_rate': u'0.00650',
            #        u'api_id': u'ebe64d72-8a75-11e4-ac1f-22000ac51de6',
            #        u'message_direction': u'outbound',
            #        u'from_number': u'1111111111',
            #        u'message_uuid': u'0936ec98-7c4c-11e4-9bd8-22000afa12b9',
            #        u'message_time': u'2014-12-05 12:27:54+05:30',
            #        u'units': 4,
            #        u'message_type': u'sms',
            #        u'resource_uri': u'/v1/Account/XXXXXXXXXXXX/Message/0936ec98-7c4c-11e4-9bd8-22000afa12b9/'
            #    }
            # )
            response = self.client.get_message(params)
            if response[1]['message_state'] in ('delivered', 'undelivered', 'failed'):
                return response[1]['message_state']
            else:
                print("Message {} status {}".format(message_id, response.status))
                return None
        except TwilioRestException as e:
            print(e)
            raise ClientException(self.identifier)

    def log(self, message_id):
        print("Plivo has sent {}".format(message_id))
