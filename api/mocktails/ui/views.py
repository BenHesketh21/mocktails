from flask import Blueprint, current_app, request, flash, render_template, send_from_directory

import json
import os

from mocktails.rules.utils import create_rules, get_all_rules
from mocktails.rules.models import Rule
from mocktails.db import get_db

ui = Blueprint('ui', 'ui', url_prefix='/ui')

@ui.route('/favicon.ico')
def favicon():
    print("hello")
    return send_from_directory(current_app.static_folder,
                               'favicon.ico')

@ui.route('/')
def view_rules():
    db = get_db(current_app)
    rules = get_all_rules(db)
    selected_rule=request.args["selected_rule"]
    return render_template('rules.html', rules=rules, selected_rule=selected_rule)

@ui.route('/add', methods=['GET', 'POST'])
def add_rule():
    print(request.form)
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
            "status_code": request.form['statusCode']
            }
        }
        new_rule = Rule(init_json_data=rule)
        created = new_rule.create_rule(db)
        if created[0] == False:
            flash("Failed to Create Rule", 'danger')
        else:
            flash("Created Rule", "success")
        return render_template('rule_form.html', page_title="Add a Rule", button_value="Add Rule") 
    return render_template('rule_form.html', page_title="Add a Rule", button_value="Add Rule") 