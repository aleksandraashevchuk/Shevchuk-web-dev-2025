import pytest
from flask import url_for
from flask_login import login_user

@pytest.fixture
def login_user_user_role(app, client, db_connector, example_roles):
    user_data = ("testuser", "123456", "Test", "T", "Tester", example_roles[0].id)
    connection = db_connector.connect()
    with connection.cursor() as cursor:
        cursor.execute(
            "INSERT INTO users(username, password_hash, first_name, middle_name, last_name, role_id) "
            "VALUES (%s, SHA2(%s, 256), %s, %s, %s, %s);",
            user_data
        )
        connection.commit()
        cursor.execute("SELECT id FROM users WHERE username = %s;", (user_data[0],))
        user_id = cursor.fetchone()[0]

    yield {"id": user_id, "username": user_data[0], "password": user_data[1]}

    with connection.cursor() as cursor:
        cursor.execute("DELETE FROM visit_logs;")
        cursor.execute("DELETE FROM users WHERE id = %s;", (user_id,))
        connection.commit()


def test_user_cannot_access_admin_page_edit(client, app, login_user_user_role):
    with app.test_request_context():
        with client.session_transaction() as session:
            session['_user_id'] = str(login_user_user_role['id'])

        response = client.get('/users/2/edit', follow_redirects=False)
        assert response.status_code in (302, 308)

        assert '/users/' in response.location

def test_user_cannot_access_admin_page_new(client, app, login_user_user_role):
    with app.test_request_context():
        with client.session_transaction() as session:
            session['_user_id'] = str(login_user_user_role['id'])

        response = client.get('/users/new', follow_redirects=False)
        assert response.status_code in (302, 308)

        assert '/users/' in response.location

def test_user_cannot_access_admin_page_delete(client, app, login_user_user_role):
    with app.test_request_context():
        with client.session_transaction() as session:
            session['_user_id'] = str(login_user_user_role['id'])

        response = client.post('/users/2/delete', follow_redirects=False)
        assert response.status_code in (302, 308)

        assert '/users/' in response.location

def test_user_cannot_access_admin_by_pages(client, app, login_user_user_role):
    with app.test_request_context():
        with client.session_transaction() as session:
            session['_user_id'] = str(login_user_user_role['id'])

        response = client.get('/logs/by_pages', follow_redirects=False)
        assert response.status_code in (302, 308)

        assert '/users/' in response.location

def test_user_cannot_access_admin_by_users(client, app, login_user_user_role):
    with app.test_request_context():
        with client.session_transaction() as session:
            session['_user_id'] = str(login_user_user_role['id'])

        response = client.get('/logs/by_pages', follow_redirects=False)
        assert response.status_code in (302, 308)

        assert '/users/' in response.location

