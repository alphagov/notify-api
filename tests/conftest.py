import pytest
from flask import Flask
import mock


@pytest.fixture
def app():
    return Flask(__name__)


@pytest.fixture
def os_environ(request):
    env_patch = mock.patch('os.environ', {})
    request.addfinalizer(env_patch.stop)

    return env_patch.start()
