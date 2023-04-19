from mocktails.db import get_db
from mocktails.mocks.utils import __mock_request

from tests.test_rules import new_rule, app, new_non_unique_rule


def test_mock_request(app):
    with app.app_context() as a:
        db = get_db(a)
        rule = new_rule(db)
        response, status_code = __mock_request(db, 'test/endpoint', 'GET', {})
        assert response == {'message': 'I am a test'}
        assert status_code == 200

def test_mock_with_no_rules(app):
    with app.app_context() as a:
        db = get_db(a)
        response, status_code = __mock_request(db, 'some/endpoint/6', 'DELETE', {})
        assert response == {"message": "Not Found"}
        assert status_code == 404

def test_wrong_method(app):
    with app.app_context() as a:
        db = get_db(a)
        rule = new_rule(db)
        response, status_code = __mock_request(db, 'test/endpoint', 'DELETE', {})
        assert response == {'message': 'Method Not Allowed'}
        assert status_code == 405

def test_new_non_unique_body_rule(app):
    with app.app_context() as a:
        db = get_db(a)
        rule = new_non_unique_rule(db)
        response1, status_code1 = __mock_request(db, 'test/endpoint', 'GET', {})
        response2, status_code2 = __mock_request(db, 'test/endpoint', 'GET', {'message': 'anything'})
        assert response1 == {'message': 'I am a test'} and status_code1 == 200
        assert response2 == {'message': 'I am a test'} and status_code2 == 200
