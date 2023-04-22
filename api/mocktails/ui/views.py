from flask import Blueprint, current_app, request, send_file, render_template, url_for

import json

from mocktails.rules.utils import create_rules
from mocktails.rules.models import Rule
from mocktails.db import get_db

ui = Blueprint('ui', 'ui', url_prefix='/ui')

@ui.route('/')
def index():
    return render_template('index.html')

@ui.route('/add', methods=['GET', 'POST'])
def add_rule():
    if request.method == "POST":
        print(request.form)
        db = get_db(current_app)
        rule = {
            "uniqueRequestBody": True if request.form['uniqueRequestBody'] == 'on' else False,
            "request": {
            "endpoint": request.form['endpoint'],
            "methods": request.form.getlist('methods'),
            "body": json.loads(request.form['requestBody'])
            },
            "response": {
            "body": json.loads(request.form['responseBody']),
            "status_code": request.form['status_code']
            }
        }
        new_rule = Rule(init_json_data=rule)
        created= new_rule.create_rule(db)
        return render_template('add.html', message=created) 
    return render_template('add.html') 