from datetime import datetime
from flask_login import FlaskLoginClient
from app import User
import pytest
import os
from flask import template_rendered
from contextlib import contextmanager
from app import app as application

@pytest.fixture
def app():
    application.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
    return application

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def client_second(app):
    return app.test_client()

@pytest.fixture
def auth_client(app):
    app.test_client_class = FlaskLoginClient
    return app.test_client(user=User('1', 'user'))

@pytest.fixture
@contextmanager
def captured_templates(app):
    recorded = []
    def record(sender, template, context, **extra):
        recorded.append((template, context))
    template_rendered.connect(record, app)
    try:
        yield recorded
    finally:
        template_rendered.disconnect(record, app)
