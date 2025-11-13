from flask import session
import datetime

def test_counter_initial_value(client):
    """Проверяет, что счётчик начинается с 1 при первом посещении"""
    response = client.get('/counter')
    assert response.status_code == 200
    assert 'Вы посетили эту страницу 1 раз' in response.text


def test_counter_increments(client):
    """Проверяет, что счётчик увеличивается при каждом посещении"""
    response = client.get('/counter')
    assert '1 раз' in response.text

    response = client.get('/counter')
    assert '2 раз' in response.text

    response = client.get('/counter')
    assert '3 раз' in response.text


def test_counter_per_session(client, client_second):
    """Проверяет, что разные сессии имеют свои счетчики"""
    client1 = client
    response1 = client1.get('/counter')
    assert '1 раз' in response1.text

    response1 = client1.get('/counter')
    assert '2 раз' in response1.text

    # Другая сессия

    client2 = client_second
    response2 = client2.get('/counter')
    assert '1 раз' in response2.text

    response1 = client1.get('/counter')
    assert '3 раз' in response1.text

    response2 = client2.get('/counter')
    assert '2 раз' in response2.text


def test_successful_login(client):
    """Проверяет код ответа после успешной аутентификации бзе редиректа"""
    response = client.post('/login', data={
        'username': 'user',
        'password': 'qwerty'
    }, follow_redirects=False)  # не следовать редиректу автоматически

    assert response.status_code == 302
    assert response.location == '/'


def test_successful_login_redirect_index(client):
    """Проверяет редирект и сообщения после успешной аутентификации"""
    with client:
        response = client.post('/login', data={
            'username': 'user',
            'password': 'qwerty'
        }, follow_redirects=True)

        assert session.get('_user_id') == '1'

        assert len(response.history) == 1
        assert response.request.path == "/"

        assert response.status_code == 200
        assert 'Это главная страница!' in response.text

        assert 'Вы успешно аутентифицированы!' in response.text
        assert 'alert-success' in response.text

def test_error_login_redirect_and_message(client):
    """Проверяет код ответа и сообщение после успешной аутентификации"""
    response = client.post('/login', data={
        'username': 'user1',
        'password': 'qwerty'
    }, follow_redirects=True)

    assert len(response.history) == 0
    assert response.request.path == "/login"

    assert response.status_code == 200

    assert 'Пользователь не найден, проверьте корректность введенных данных' in response.text


def test_secret_link_in_header_after_login(client):
    """Проверяем, что ссылка на секретную страницу появляется в шапке после входа"""
    response = client.get('/')
    assert 'Секретная страница' not in response.text

    client.post('/login', data={
        'username': 'user',
        'password': 'qwerty'
    }, follow_redirects=True)

    response = client.get('/')
    assert 'Секретная страница' in response.text
    assert 'href="/secret"' in response.text

def test_go_to_secret_page_before_login(client):
    """Проверяем, что секретная страница не отображается после неуспешной аутентификации и выполняется редирект на страницу авторизации"""

    client.post('/login', data={
        'username': 'user1',
        'password': 'qwerty'
    }, follow_redirects=True)

    response = client.get('/secret', follow_redirects=True)

    assert len(response.history) == 1
    assert response.request.path == "/login"
    assert 'Для доступа к запрашиваемой странице необходимо пройти процедуру аутентификации!' in response.text

def test_go_to_secret_page_after_login(client):
    """Проверяем, что секретная страница отображается после успешной аутентификации"""

    client.post('/login', data={
        'username': 'user',
        'password': 'qwerty'
    }, follow_redirects=True)

    response = client.get('/secret')
    assert response.status_code == 200
    assert 'Эта страница видна только аутентифицированным пользователям.' in response.text


def test_go_to_secret_page_after_login_auto(client):
    """Проверяем, что при аутентификации после неудачной попытки доступа к секретной странице пользователь автоматически перенаправляется на секретную страницу"""
    response = client.get('/secret', follow_redirects=False)
    assert response.status_code == 302
    assert '/login?next=%2Fsecret' in response.location

    login_response = client.post(response.location, data={
        'username': 'user',
        'password': 'qwerty'
    }, follow_redirects=True)

    assert len(login_response.history) == 1
    assert login_response.request.path == "/secret"
    assert 'Эта страница видна только аутентифицированным пользователям.' in login_response.text


def test_remember_me_cookie_expiry_date(client):
    """Проверяем, что соответствующий куки есть и дата истечения куки равна текущей дате + 1 год"""

    client.post('/login', data={
        'username': 'user',
        'password': 'qwerty',
        'remember_me': 'on'
    }, follow_redirects=True)

    cookie = client.get_cookie('remember_token')
    assert cookie is not None
    assert cookie.expires is not None

    expiry_date = cookie.expires.astimezone(datetime.UTC).date()
    expected_date = (datetime.datetime.now(datetime.UTC) + datetime.timedelta(days=365)).date()

    assert expiry_date == expected_date

def test_navbar_links_visibility(client, auth_client):
    """Проверяем видимость ссылок в навигационной панели"""
    response = client.get('/')
    assert response.status_code == 200
    assert 'Войти' in response.text
    assert 'Выйти' not in response.text
    assert 'Секретная страница' not in response.text

    response = auth_client.get('/')
    assert response.status_code == 200
    assert 'Войти' not in response.text
    assert 'Выйти' in response.text
    assert 'Секретная страница' in response.text

