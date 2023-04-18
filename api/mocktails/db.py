from tests.redis_mock import FakeRedisClient

from flask_redis import FlaskRedis
from flask import current_app

def get_db(app):
    if current_app.testing:
        current_app.logger.debug("Using Test Redis Client")
        redis_client = FakeRedisClient()
        redis_client.clear_hashes()
    else:
        current_app.logger.debug("Opening connection to Redis")
        redis_client = FlaskRedis(current_app, decode_responses=True)

    return redis_client