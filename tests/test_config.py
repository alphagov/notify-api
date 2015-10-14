from app import init_app


def test_init_app_updates_known_config_options(notify_api, os_environ, notify_config):
    notify_api.config['MY_SETTING'] = 'foo'
    os_environ.update({'MY_SETTING': 'bar'})

    init_app(notify_api)

    assert notify_api.config['MY_SETTING'] == 'bar'


def test_init_app_ignores_unknown_options(notify_api, os_environ, notify_config):
    os_environ.update({'MY_OTHER_SETTING': 'bar'})

    init_app(notify_api)
    assert 'MY_OTHER_SETTING' not in notify_api.config


def test_init_app_converts_truthy_to_bool(notify_api, os_environ, notify_config):
    notify_api.config['MY_SETTING'] = True
    os_environ.update({'MY_SETTING': 'false'})

    init_app(notify_api)

    assert notify_api.config['MY_SETTING'] is False
