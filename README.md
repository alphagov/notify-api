[![Build Status](https://api.travis-ci.org/alphagov/notify-api.svg?branch=master)](https://api.travis-ci.org/alphagov/notify-api.svg?branch=master)

# notify-api [ALPHA]
Alpha for notify API. Sends emails/sms/printed content on behalf of government.

### technology

Using python3:
- brew install python3

VirtualEnvWrapper
- http://virtualenvwrapper.readthedocs.org/en/latest/command_ref.html

Setting up a virtualenvwrapper for python3
mkvirtualenv -p /usr/local/bin/python3 notify-api

-- note using python3/pep3 for dependencies

Setup - run bootstrap
./scripts/bootstrap.sh

Links from:
python application.py list_routes

uses pep8 for syntax checking
-
