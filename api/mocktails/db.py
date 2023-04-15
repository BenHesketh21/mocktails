from flask_redis import FlaskRedis

from flask import current_app

def get_db(app):
    
    redis_client = FlaskRedis(current_app, decode_responses=True)

    return redis_client