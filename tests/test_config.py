from app import init_app


def test_init_app_updates_known_config_options(app, os_environ):
    with app.app_context():
        app.config['MY_SETTING'] = 'foo'
        os_environ.update({'MY_SETTING': 'bar'})

        init_app(app)

        assert app.config['MY_SETTING'] == 'bar'


def test_init_app_ignores_unknown_options(app, os_environ):
    with app.app_context():
        os_environ.update({'MY_SETTING': 'bar'})

        init_app(app)

        assert 'MY_SETTING' not in app.config


def test_init_app_converts_truthy_to_bool(app, os_environ):
    with app.app_context():
        app.config['MY_SETTING'] = True
        os_environ.update({'MY_SETTING': 'false'})

        init_app(app)

        assert app.config['MY_SETTING'] is False
