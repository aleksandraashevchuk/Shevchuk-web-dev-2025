import os
from flask import Flask
from .extensions import db, login_manager

def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=False)

    app.config.from_pyfile('config.py', silent=False)
    if test_config:
        app.config.update(test_config)

    db.init_app(app)
    login_manager.init_app(app)

    from .cli import init_db_command
    app.cli.add_command(init_db_command)

    # контекст приложения - временная зона, которая знает какое приложение активно
    with app.app_context():
        from . import auth, users
        app.register_blueprint(auth.bp)
        app.register_blueprint(users.bp)

    return app