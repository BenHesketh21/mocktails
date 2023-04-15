from flask_redis import FlaskRedis
from fakeredis import FakeStrictRedis
from flask import current_app

def get_db(app):

    if current_app.testing:
        current_app.logger.debug("Using Test Redis Client")
        redis_client = FakeStrictRedis()
    else:
        current_app.logger.debug("Opening connection to Redis")
        redis_client = FlaskRedis(current_app, decode_responses=True)

    return redis_client