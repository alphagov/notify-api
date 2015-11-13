from flask import json

from app.connectors.access_queue import sendMessagesToQueue, getMessagesFromQueue


def test_sendMessages_should_add_messages_to_queue(notify_api):
    notification = {'to': 'jo@example.com',
                    'from': 'sue@example.gov.uk',
                    'subject': 'notification subject',
                    'message': 'notification message'}
    messages = [notification]
    sendMessagesToQueue('email', messages)

    read = getMessagesFromQueue()
    for r in read:
        print("** {}".format(r))
        assert r.body == json.dumps(notification)
        assert r.message_attributes.get('type').get('StringValue') == 'email'
        r.delete()
