[![Build Status](https://api.travis-ci.org/alphagov/notify-api.svg?branch=master)](https://api.travis-ci.org/alphagov/notify-api.svg?branch=master)

# GOVUK Notify API [ALPHA]

API for the alpha for the GOVUK Notify platform.

This code delivers a very early version of what a notifications API might look like. It is in alpha and the code should
not be considered supported or production ready.

This API provides a wrapper around 3rd party suppliers of email and SMS APIs, allowing clients to use this API as a 
proxy onto those APIs. Responses from this API aim to consistent regardless of the underlying API call.
 
Additionally it provides various other method calls to manage the platform, with regards to users, domain model and so on.


## Installing

This is a [python](https://www.python.org/) application that utilises [flask](http://flask.pocoo.org/) as it's application framework.

#### Python version
This is a python 3 application. It has not been run against any version of python 2.x

    brew install python3

#### Database

This application uses postgres as it's database. It has been developed against [Postgres app](http://postgresapp.com/).

Once installed ensure that the `createdb` postgres command is on your path.

#### Dependency management

This is done through [pip](pip.readthedocs.org/) and [virtualenv](https://virtualenv.readthedocs.org/en/latest/). In practise we have used
[VirtualEnvWrapper](http://virtualenvwrapper.readthedocs.org/en/latest/command_ref.html) for our virtual environemnts.

Setting up a virtualenvwrapper for python3
    
    mkvirtualenv -p /usr/local/bin/python3 notify-api

#### Setup

The boostrap script will set the application up. *Ensure you have activated the virtual environment first.*

    ./scripts/bootstrap.sh
    
This will

* Use pip to install dependencies.
* Create the database, both test and real schemas.
* Apply the database migrations.

#### Tests

The `./scripts/run_tests.py` script will run all the tests. [py.test](http://pytest.org/latest/) is used for testing.

Running tests will also apply syntax checking, using [pep8](https://www.python.org/dev/peps/pep-0008/).

Uncommenting the following lines in `run_tests.py` will apply code coverage:

    #  py.test --cov=app tests/
    #  display_result $? 2 "Code coverage"
    

### URLs

All the application URLs can be displayed by running:

    python application.py list_routes
    
    

### Start job scheduler
The job scheduler reads the notifications from the queue and sends them via a provider. 
You will need to ask a member of the team for the export values below.

    export FROM_NUMBER=x
    export TWILIO_ACCOUNT_SID=x
    export TWILIO_AUTH_TOKEN=x
    export TWILIO_NUMBER=GOV
    export PLIVO_ACCOUNT_SID=x
    export PLIVO_AUTH_TOKEN=x
    export SENDGRID_API_KEY=x
    export SENDGRID_USERNAME=x
    export PYTHONPATH=.
    AWS_ACCESS_KEY_ID=x
    AWS_SECRET_ACCESS_KEY=x
    python app/job/job_schedules.py
 

### Domain model

All the domain models are defined in the [models.py](https://github.com/alphagov/notify-api/blob/master/app/models.py) file.

In essence this application is a RESTful API over that set of domain objects.

* __Notifications.__ The core of Notify is the notion of a notification. Each notification encapsulates a message sent to a user.
    
* __Jobs.__ Notifications are organised by jobs. A job can contain 1 or more notifications. 
    
* __Services.__ Jobs are created on behalf of a service. A service is a Government transaction that requires notifications to be sent. An example
     could be MOT reminders or receipt of supporting documentation in a student loads application.

* __Usage.__ This is used to record the number of notifications sent, per day, per service.

* __Token.__ Tokens is the API credentials required to send notifications for this service.

* __Organisations.__ This is not a core feature of the platform for alpha, but services could be grouped under organisations in the future.

* __User.__ User objects relate to use of the [notify-frontend](https://github.com/alphagov/notify-frontend) application. These are the user accounts. These are mapped to service via
the user_to_service mapping table. Unless a user has a relationship with a service, they cannot access that service in the admin tools.


### Using the API

It is recommended the API is accessed via the [client library](https://github.com/alphagov/notify-api-client).

The expectation is that services will be configured via the web interface. All API endpoints relating to creating and maintaing users/services and so on will be made private in the future and should not be considered supported.

### Requests

To send a notification you require the credentials for the service you want to send a notification on behalf of. These can be determined through the administration app.

A curl example call is constructed as follows:

    curl 
        -H"Authorization: Bearer service-api-token" 
        -H"Content-type: application/json"  
        -X POST 
        https://api-url/sms/notification 
        -d '{
                "notification": {
                    "to":"mobile-number", 
                    "message":"This is the message"
                }
            }'

        curl
        -H"Authorization: Bearer 1"
        -H"Content-type: application/json"
        -X POST
        https://api-url/email/notification
        -d '{
                "notification": {
                    "to":"jo@example.com",
                     "from":"service@example.gov.uk",
                     "subject":"Email subject",
                     "message":"This is the message"
                }
            }'

Where:

* "mobile-number" is the mobile phone number to deliver to
    * Only UK mobiles are supported
    * Must start with +44
    * Must not have leading zero
    * Must not have any whitespace, punctuation etc.
    * valid formt is +447777111222
    
* "message" is the text to send
    * Must be between 1 and 160 characters in length
    

With optional fields:
    
    curl 
        -H"Authorization: Bearer service-api-token" 
        -H"Content-type: application/json"  
        -X POST 
        https://api-url/sms/notification 
        -d '{
                "notification": {
                    "to":"mobile-number", 
                    "message":"This is the message", 
                    "jobId":100, 
                    "description":"Description of the job"
                }
            }'
    
    
* `jobId` is used to group notifications together. A job will be created if no job ID is supplied. If a job id is supplied notifications will be associated with that job.
If no job exists with that ID is is an error.

* `description` is used to give a meaningful name to the job relating to this notification.

    
### Responses

#### Success

    {
        "notification": {
            "createdAt": "2015-11-03T09:37:27.414363Z",
            "id": 100,
            "jobId": 65,
            "message": "This is the message",
            "method": "sms",
            "status": "created",
            "to": "+449999999999"
        }
    }
   
#### Errors
   
Error will be provided as JSON.
   
All errors have an `error` element providing a textual description of the error.
Additionally error responses may provide an `error_details` array containing per field errors, in the case of validation errors. 
   
#####Validation error
    
    {
        "error": "Invalid JSON",
        "error_details": [{
                "key": "description",
                "message": "'' is too short"
        }]
    }

* `error` describes the overall error condition
* `error_details` provides per field validation errors

#####Authentication error

    {
        "error": "Forbidden, invalid bearer token provided"
    }
    
* `error` describes the overall error condition


##### Codes

* 201 - notification created
* 400 - Bad request - invalid JSON / Failed validation
* 401 - Missing token
* 403 - Invalid token
* 429 - Usage exceeded

