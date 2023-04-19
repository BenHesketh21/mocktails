from flask import Blueprint, current_app, request, send_file, render_template


ui = Blueprint('ui', 'ui', url_prefix='/ui')

@ui.route('/')
def index():
    return render_template('index.html')

@ui.route('/add')
def add_rule():
    return render_template('add.html')