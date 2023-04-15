import os
import json
from logging.config import dictConfig

from flask import Flask

from mocktails.rules import rules, create_rules
from mocktails.mocks import mocks
from mocktails.rules_config import import_data


def create_app(test_config=None):
    # create and configure the app
    
    dictConfig({
        'version': 1,
        'formatters': {'default': {
            'format': 'time=%(asctime)s level=%(levelname)s component=%(module)s message=%(message)s',
        }},
        'handlers': {'wsgi': {
            'class': 'logging.StreamHandler',
            'stream': 'ext://flask.logging.wsgi_errors_stream',
            'formatter': 'default'
        }},
        'root': {
            'level': 'INFO',
            'handlers': ['wsgi']
        }
    })

    app = Flask(__name__, instance_relative_config=True)
    
    app.config.from_object('mocktails.settings')
    app.config.from_prefixed_env()

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    print(app.config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass
    
    app.register_blueprint(rules)
    app.register_blueprint(mocks)

    if app.config["IMPORT_DATA"] == True:
        with app.app_context():
            import_data(app.config["RULE_CONFIG_FILE"])

    return app