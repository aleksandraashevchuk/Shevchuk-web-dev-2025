from functools import reduce
from collections import namedtuple
import logging
import pytest
import mysql.connector
from app import create_app
from app.db import DBConnector
from app.repositories import RoleRepository
from app.repositories import UserRepository
from app.repositories import LogsRepository

# Я реализовал тестирование функционала уже в созданной отдельной базе данных (специально для тестов),
# поэтому нет необходимости каждый раз создавать новую базу данных. Вместо этого, я каждый раз при запуске теста -
# создаю необходимые таблицы, а по завершении - удаляю их.

TEST_DB_CONFIG = {
    'MYSQL_USER': 'l90858az_webtest',
    'MYSQL_PASSWORD': '2185kaF%1ady',
    'MYSQL_HOST': 'l90858az.beget.tech',
    'MYSQL_DATABASE': 'l90858az_webtest',
}


def get_connection(app):
    return mysql.connector.connect(
        user=app.config['MYSQL_USER'],
        password=app.config['MYSQL_PASSWORD'],
        host=app.config['MYSQL_HOST'],
        database=app.config['MYSQL_DATABASE']
    )


def setup_db(app):
    logging.getLogger().info("SET UP THE DATABASE SCHEMA...")

    with app.open_resource('schema_set_up_for_tests.sql') as f:
        schema_sql = f.read().decode('utf8')

    connection = get_connection(app)
    with connection.cursor() as cursor:
        for _ in cursor.execute(schema_sql, multi=True):
            pass

    connection.commit()
    connection.close()


def teardown_db(app):
    logging.getLogger().info("DROP THE DATABASE SCHEMA...")
    with app.open_resource('schema_delete_for_tests.sql') as f:
        schema_sql = f.read().decode('utf8')

    connection = get_connection(app)
    with connection.cursor() as cursor:
        for _ in cursor.execute(schema_sql, multi=True):
            pass

    connection.commit()
    connection.close()


@pytest.fixture(scope='session')
def app():
    return create_app(TEST_DB_CONFIG)


@pytest.fixture(scope='session')
def db_connector(app):
    setup_db(app)
    with app.app_context():
        connector = DBConnector(app)
        yield connector
        connector.disconnect()
    teardown_db(app)


@pytest.fixture
def role_repository(db_connector):
    return RoleRepository(db_connector)


@pytest.fixture
def existing_role(db_connector):
    data = (1, 'admin')
    row_class = namedtuple('Row', ['id', 'name'])
    role = row_class(*data)

    connection = db_connector.connect()

    with connection.cursor() as cursor:
        query = 'INSERT INTO roles(id, name) VALUES (%s, %s);'
        cursor.execute(query, data)
        connection.commit()

    yield role

    with connection.cursor() as cursor:
        query = 'DELETE FROM roles WHERE id=%s;'
        cursor.execute(query, (role.id,))
        connection.commit()

@pytest.fixture
def existing_role_admin(db_connector):
    data = (2, 'user')
    row_class = namedtuple('Row', ['id', 'name'])
    role = row_class(*data)

    connection = db_connector.connect()

    with connection.cursor() as cursor:
        query = 'INSERT INTO roles(id, name) VALUES (%s, %s);'
        cursor.execute(query, data)
        connection.commit()

    yield role

    with connection.cursor() as cursor:
        query = 'DELETE FROM roles WHERE id=%s;'
        cursor.execute(query, (role.id,))
        connection.commit()



@pytest.fixture
def nonexisting_role_id():
    return 1


@pytest.fixture
def example_roles(db_connector):
    data = [(1, 'admin'), (2, 'user')]
    row_class = namedtuple('Row', ['id', 'name'])
    roles = [row_class(*row_data) for row_data in data]

    connection = db_connector.connect()

    with connection.cursor() as cursor:
        placeholders = ', '.join(['(%s, %s)' for _ in range(len(data))])
        query = f"INSERT INTO roles(id, name) VALUES {placeholders};"
        cursor.execute(query, reduce(lambda seq, x: seq + list(x), data, []))
        connection.commit()

    yield roles

    with connection.cursor() as cursor:
        role_ids = ', '.join([str(role.id) for role in roles])
        query = f"DELETE FROM roles WHERE id IN ({role_ids});"
        cursor.execute(query)
        connection.commit()


@pytest.fixture
def user_repository(db_connector):
    return UserRepository(db_connector)


@pytest.fixture
def existing_user(db_connector, existing_role):
    data = (1, 'user1', 'password123', 'Ivan', 'Ivanovich', 'Ivanon', existing_role.id)
    row_class = namedtuple('Row', ['id', 'username', 'password_hash', 'first_name', 'middle_name', 'last_name', 'role_id'])
    user = row_class(*data)

    connection = db_connector.connect()

    with connection.cursor() as cursor:
        query = (
            "INSERT INTO users (id, username, password_hash, first_name, middle_name, last_name, role_id) "
            "VALUES (%s, %s, SHA2(%s, 256), %s, %s, %s, %s);"
        )
        cursor.execute(query, data)
        connection.commit()

    yield user

    with connection.cursor() as cursor:
        query = "DELETE FROM users WHERE id = %s;"
        cursor.execute(query, (user.id,))
        connection.commit()

@pytest.fixture
def example_users(db_connector, example_roles):
    data = [
        (1, 'user1', 'password123', 'Ivan', 'Ivanovich', 'Ivanon', example_roles[0].id),
        (2, 'user2', 'password456', 'Alexey', 'Dmitrievich', 'Nagorniy', example_roles[1].id)
    ]
    row_class = namedtuple('Row', ['id', 'username', 'password_hash', 'first_name', 'middle_name', 'last_name', 'role_id'])
    users = [row_class(*row_data) for row_data in data]

    connection = db_connector.connect()

    with connection.cursor() as cursor:
        placeholders = ', '.join(['(%s, %s, SHA2(%s, 256), %s, %s, %s, %s)' for _ in range(len(data))])
        query = f"INSERT INTO users(id, username, password_hash, first_name, middle_name, last_name, role_id) VALUES {placeholders};"
        cursor.execute(query, reduce(lambda seq, x: seq + list(x), data, []))
        connection.commit()

    yield users

    with connection.cursor() as cursor:
        user_ids = ', '.join([str(user.id) for user in users])
        query = f"DELETE FROM users WHERE id IN ({user_ids});"
        cursor.execute(query)
        connection.commit()

@pytest.fixture
def nonexisting_user_id():
    return 9999


@pytest.fixture
def created_user(db_connector, existing_role):
    username = "testuser"
    password = "123456"
    user_data = (username, password, "Vyacheslav", "", "Samokhvalov", existing_role.id)

    connection = db_connector.connect()
    with connection.cursor() as cursor:
        query = (
            "INSERT INTO users(username, password_hash, first_name, middle_name, last_name, role_id) "
            "VALUES (%s, SHA2(%s, 256), %s, %s, %s, %s);"
        )
        cursor.execute(query, user_data)
        connection.commit()

        cursor.execute("SELECT id FROM users WHERE username = %s;", (username,))
        user_id = cursor.fetchone()[0]

    row_class = namedtuple('User', ['id', 'username', 'password', 'first_name', 'middle_name', 'last_name', 'role_id'])
    user = row_class(user_id, *user_data)

    yield user

    with connection.cursor() as cursor:
        cursor.execute("DELETE FROM users WHERE id = %s;", (user.id,))
        connection.commit()


@pytest.fixture
def updated_user(db_connector, existing_user):
    new_data = ("Updated", "X", "Y", existing_user.role_id)

    connection = db_connector.connect()
    with connection.cursor() as cursor:
        cursor.execute(
            "UPDATE users SET first_name=%s, middle_name=%s, last_name=%s, role_id=%s WHERE id=%s;",
            (*new_data, existing_user.id)
        )
        connection.commit()

    row_class = namedtuple('User', ['id', 'username', 'password', 'first_name', 'middle_name', 'last_name', 'role_id'])
    updated = row_class(existing_user.id, existing_user.username, existing_user.password_hash, *new_data)

    return updated

@pytest.fixture
def client(app):
    return app.test_client()
