from mocktails import create_app
from mocktails.rules.utils import get_all_rules, create_rules
from mocktails.rules.models import Rule
from mocktails.db import get_db

import pytest
import json

@pytest.fixture()
def app():
    app = create_app()
    app.config.update({
        "TESTING": True
    })
    yield app

@pytest.fixture()
def client(app):
    return app.test_client()

def new_rule(db):
    rule = Rule(init_json_data={
        'name': 'Test Rule',
        'uniqueRequestBody': True, 
        'request': {
            'body': {}, 
            'endpoint': '/test/endpoint', 
            'methods': ['GET']
        }, 
        'response': {
            'body': {
                'message': 'I am a test'
            }, 
            'status_code': 200
        }
    })
    rule.create_rule(db)
    return rule

def new_non_unique_rule(db):
    rule = Rule(init_json_data={
        'name': 'Test Rule',
        'uniqueRequestBody': False, 
        'request': {
            'body': {}, 
            'endpoint': '/test/endpoint', 
            'methods': ['GET']
        }, 
        'response': {
            'body': {
                'message': 'I am a test'
            }, 
            'status_code': 200
        }
    })
    rule.create_rule(db)
    return rule

def test_get_empty_rules(app):
    with app.app_context() as a:

        db = get_db(a) 
        rules = get_all_rules(db)
        assert rules == {}

def test_add_rule(app):
    with app.app_context() as a:
        db = get_db(a)
        id = 'REVMRVRFL3NvbWUvZW5kcG9pbnQvNnt9'
        expected = {
            'name': 'Test Rule',
            'uniqueRequestBody': True, 
            'request': {
                'body': {}, 
                'endpoint': '/some/endpoint/6', 
                'methods': ['DELETE']
            }, 
            'response': {
                'body': {
                    'boom': 'I AM DELETING'
                }, 
                'status_code': 200
            }
        }
        created = create_rules(db, [{
            'name': 'Test Rule',
            'uniqueRequestBody': True, 
            'request': {
                'body': {}, 
                'endpoint': '/some/endpoint/6', 
                'methods': ['DELETE']
            }, 
            'response': {
                'body': {
                    'boom': 'I AM DELETING'
                }, 
                'status_code': 200
            }
        }])
        assert created == {id: expected, 'errors': []}

def test_generation_of_id(app):
    with app.app_context() as a:
        db = get_db(a)
        rule = new_rule(db)
        id = rule.generate_rule_id()
        assert id == "R0VUL3Rlc3QvZW5kcG9pbnR7fQ==" 

def test_uniqueness_of_rules(app):
    with app.app_context() as a:
        db = get_db(a)
        rule1 = new_rule(db)
        created = rule1.create_rule(db)
        assert created == (False, rule1.id)

def test_delete_rule(app):
    with app.app_context() as a:
        db = get_db(a)
        rule1 = new_rule(db)
        deleted = rule1.delete_rule(db)
        assert deleted == True
        assert db.hget("rules", rule1.id) == None

def test_update_rule(app):
    with app.app_context() as a:
        db = get_db(a)
        rule1 = new_rule(db)
        updated_rule={
            'name': 'Test Rule',
            'uniqueRequestBody': True, 
            'request': {
                'body': {
                    'message': 'hello'
                }, 
                'endpoint': '/some/endpoint/6', 
                'methods': ['DELETE']
            }, 
            'response': {
                'body': {
                    'boom': 'I AM DELETING'
                }, 
                'status_code': 200
            }
        }
        updated = rule1.update_rule(db, updated_rule)
        assert updated == (True, 'Updated REVMRVRFL3NvbWUvZW5kcG9pbnQvNnsnbWVzc2FnZSc6J2hlbGxvJ30=')

def test_generate_existing_rule(app):
    with app.app_context() as a:
        db = get_db(a)
        rule1 = new_rule(db)
        existing_rule = Rule(rule_id=rule1.id, db=db)
        assert existing_rule.json_data == rule1.json_data

def test_rule_with_bad_init():
    try:
        bad_rule = Rule()
    except BaseException as e:
        print(e)
        assert e.args[0] == "You must set init_json or (the rule_id with the db context)"

def test_rule_with_bad_init_2(app):
    with app.app_context() as a:
        db = get_db(a)
        try:
            bad_rule = Rule(rule_id="IDONTEXIST", db=db)
        except BaseException as e:
            assert e.args[0] == "Rule IDONTEXIST Doesn't exist"

def test_generate_request_without_body(app):
    with app.app_context() as a:
        db = get_db(a) 
        rule = Rule(init_json_data={
            'name': 'Test Rule',
            'uniqueRequestBody': True, 
            'request': {
                'endpoint': '/some/endpoint/6', 
                'methods': ['DELETE']
            }, 
            'response': {
                'body': {
                    'boom': 'I AM DELETING'
                }, 
                'status_code': 200
            }
        })
        
        rule.create_rule(db)
        assert rule.json_data == {
            'REVMRVRFL3NvbWUvZW5kcG9pbnQvNg==': {
                'name': 'Test Rule',
                'request': {
                    'endpoint': '/some/endpoint/6', 
                    'methods': ['DELETE']
                }, 
                'response': {
                    'body': {
                        'boom': 'I AM DELETING'
                    }, 
                    'status_code': 200
                }, 
                'uniqueRequestBody': True
            }
        }

def test_delete_when_not_exists(app):
    with app.app_context() as a:
        db = get_db(a)
        rule = Rule(init_json_data={
                'name': 'Test Rule',
                'uniqueRequestBody': True, 
                'request': {
                    'endpoint': '/some/endpoint/6', 
                    'methods': ['DELETE']
                }, 
                'response': {
                    'body': {
                        'boom': 'I AM DELETING'
                    }, 
                    'status_code': 200
                }
            })
        deleted = rule.delete_rule(db)
        assert deleted == False

def test_update_when_not_exists(app):
    with app.app_context() as a:
        db = get_db(a)
        rule = Rule(init_json_data={
                'name': 'Test Rule',
                'uniqueRequestBody': True, 
                'request': {
                    'endpoint': '/some/endpoint/6', 
                    'methods': ['DELETE']
                }, 
                'response': {
                    'body': {
                        'boom': 'I AM DELETING'
                    }, 
                    'status_code': 200
                }
            })
        updated = rule.update_rule(db, {})
        assert updated == (False, None)
