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
        }}
    })

    app = Flask(__name__, instance_relative_config=True)
    
    app.config.from_object('mocktails.settings')
    app.config.from_prefixed_env()

    if app.testing == True:
        app.config.update({
            "TESTING": True,
            "RULE_CONFIG_FILE": "./test.json",
            "IMPORT_DATA": True
        })

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass
    
    app.register_blueprint(rules)
    app.register_blueprint(mocks)

    if app.config["IMPORT_DATA"] == True:
        app.logger.debug("Importing Data")
        with app.app_context():
            import_data(app.config["RULE_CONFIG_FILE"])

    return app