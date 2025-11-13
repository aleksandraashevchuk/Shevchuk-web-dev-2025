def test_args_page(client):
    """ Проверяет, что страница корректно отображает переданные параметры """
    response = client.get("/args?param1=value1&param2=value2")

    assert response.status_code == 200
    assert "param1" in response.text
    assert "value1" in response.text
    assert "param2" in response.text
    assert "value2" in response.text

def test_headers_display(client):
    """ Проверяет, что на странице отображаются все переданные заголовки запроса """
    headers = {
        "X-Custom-Header": "TestValue"
    }
    response = client.get("/headers", headers=headers)

    assert response.status_code == 200
    assert "Заголовки запроса" in response.text
    assert "X-Custom-Header" in response.text
    assert "TestValue" in response.text

def test_headers_no_headers(client):
    """ Проверяет, что если заголовки не передаются, то страница всё равно отображается """
    response = client.get("/headers")

    assert response.status_code == 200
    assert "Заголовки запроса" in response.text
    assert "User-Agent" in response.text
    assert "X-Custom-Header" not in response.text

def test_multiple_headers(client):
    """ Проверяет, что несколько заголовков отображаются """
    headers = {
        "X-First-Header": "FirstValue",
        "X-Second-Header": "SecondValue",
        "X-Third-Header": "ThirdValue"
    }
    response = client.get("/headers", headers=headers)

    assert response.status_code == 200
    assert "Заголовки запроса" in response.text
    assert "X-First-Header" in response.text
    assert "FirstValue" in response.text
    assert "X-Second-Header" in response.text
    assert "SecondValue" in response.text
    assert "X-Third-Header" in response.text
    assert "ThirdValue" in response.text


def test_delete_cookie(client):
    """ Проверяет, что куки корректно создаются и удаляются """

    response = client.get('/cookies')
    assert response.status_code == 200
    assert "Vyacheslav" not in response.data.decode()

    response = client.get('/cookies')
    assert response.status_code == 200
    assert "Vyacheslav" in response.data.decode()

    response = client.get('/cookies')
    assert response.status_code == 200
    assert "Vyacheslav" not in response.data.decode()

    response = client.get('/cookies')
    assert response.status_code == 200
    assert "Vyacheslav" in response.data.decode()

def test_form_display(client):
    """Проверяет, что форма отображается правильно на странице"""
    response = client.get('/form')
    assert response.status_code == 200
    assert 'Тема' in response.text
    assert 'Текст' in response.text
    assert 'Отправить' in response.text

def test_form_submission(client):
    """Проверяет, что введённые данные отображаются после отправки формы"""
    response = client.post('/form', data={
        'theme': 'Test Theme',
        'text': 'Test text content'
    })

    assert response.status_code == 200
    assert 'Test Theme' in response.text
    assert 'Test text content' in response.text

def test_form_with_prefilled_data(client):
    """Проверяет, что форма содержит введённые ранее данные после отправки"""
    response = client.post('/form', data={
        'theme': 'Test Theme',
        'text': 'Test text content'
    })

    assert response.status_code == 200
    assert '<input type="text" name="theme" value="Test Theme">' in response.text
    assert '<textarea name="text" id="">Test text content</textarea>' in response.text

def test_phone_validation_success1(client):
    """ Проверяет, что при вводе корректного номера телефона возвращается отформатированный номер """
    response = client.post('/form-phone', data={'phone': '+7 (123) 456-75-90'})
    assert response.status_code == 200
    assert 'Форматированный номер: 8-123-456-75-90' in response.text
    assert 'is-invalid' not in response.text
    assert 'invalid-feedback' not in response.text

def test_phone_validation_success2(client):
    """ Проверяет, что при вводе корректного номера телефона возвращается отформатированный номер """
    response = client.post('/form-phone', data={'phone': '8(123)4567590'})
    assert response.status_code == 200
    assert 'Форматированный номер: 8-123-456-75-90' in response.text
    assert 'is-invalid' not in response.text
    assert 'invalid-feedback' not in response.text

def test_phone_validation_success3(client):
    """ Проверяет, что при вводе корректного номера телефона возвращается отформатированный номер """
    response = client.post('/form-phone', data={'phone': '123.456.75.90'})
    assert response.status_code == 200
    assert 'Форматированный номер: 8-123-456-75-90' in response.text
    assert 'is-invalid' not in response.text
    assert 'invalid-feedback' not in response.text

def test_phone_validation_success4(client):
    """ Проверяет, что при вводе корректного номера телефона возвращается отформатированный номер """
    response = client.post('/form-phone', data={'phone': '7.123.456.75.90'})
    assert response.status_code == 200
    assert 'Форматированный номер: 8-123-456-75-90' in response.text
    assert 'is-invalid' not in response.text
    assert 'invalid-feedback' not in response.text

def test_phone_validation_success5(client):
    """ Проверяет, что при вводе корректного номера телефона возвращается отформатированный номер """
    response = client.post('/form-phone', data={'phone': '8.123.456.75.90'})
    assert response.status_code == 200
    assert 'Форматированный номер: 8-123-456-75-90' in response.text
    assert 'is-invalid' not in response.text
    assert 'invalid-feedback' not in response.text

def test_phone_validation_invalid_characters(client):
    """ Проверяет, что при вводе номера телефона с недопустимыми символами выводится ошибка """
    response = client.post('/form-phone', data={'phone': '8(999)*123-45-67'})
    assert response.status_code == 200
    assert 'Недопустимый ввод. В номере телефона встречаются недопустимые символы.' in response.text
    assert 'is-invalid' in response.text
    assert 'invalid-feedback' in response.text

def test_phone_validation_invalid_length1(client):
    """ Проверяет, что при вводе номера телефона неправильной длины выводится ошибка """
    response = client.post('/form-phone', data={'phone': '89991'})
    assert response.status_code == 200
    assert 'Недопустимый ввод. Неверное количество цифр.' in response.text
    assert 'is-invalid' in response.text
    assert 'invalid-feedback' in response.text


def test_phone_validation_invalid_length2(client):
    """ Проверяет, что при вводе номера телефона неправильной длины выводится ошибка """
    response = client.post('/form-phone', data={'phone': '899911111111'})
    assert response.status_code == 200
    assert 'Недопустимый ввод. Неверное количество цифр.' in response.text
    assert 'is-invalid' in response.text
    assert 'invalid-feedback' in response.text

def test_phone_validation_empty(client):
    """ Проверяет, что при вводе пустого поля телефона не происходит форматирования """
    response = client.post('/form-phone', data={'phone': ''})
    assert response.status_code == 200
    assert 'is-invalid' in response.text
    assert 'invalid-feedback' in response.text
    assert 'Недопустимый ввод. В номере телефона встречаются недопустимые символы.' in response.text







