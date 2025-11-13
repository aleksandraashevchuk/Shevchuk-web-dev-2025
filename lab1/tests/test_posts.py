def test_posts_index(client):
    """ Проверяет, что главная страница списка постов доступна и содержит заголовок 'Последние посты' """
    response = client.get("/posts")
    assert response.status_code == 200
    assert "Последние посты" in response.text


def test_posts_index_template(client, captured_templates, mocker, posts_list):
    """ Проверяет, что при рендеринге страницы списка постов используется правильный шаблон и передаются нужные данные """
    with captured_templates as templates:
        mocker.patch("app.posts_list", return_value=posts_list, autospec=True)

        _ = client.get('/posts')
        assert len(templates) == 1
        template, context = templates[0]
        assert template.name == 'posts.html'
        assert context['title'] == 'Посты'
        assert len(context['posts']) == 1


def test_post_page_template(client, captured_templates, mocker, posts_list):
    """ Проверяет, что при рендеринге страницы отдельного поста используется шаблон 'post.html' """
    with captured_templates as templates:
        mocker.patch("app.posts_list", return_value=posts_list)

        response = client.get('/posts/0')
        assert response.status_code == 200
        assert len(templates) == 1
        template, context = templates[0]
        assert template.name == 'post.html'
        assert context['post']['title'] == 'Заголовок поста'


def test_post_content(client, mocker, posts_list):
    """ Проверяет, что на странице поста отображаются заголовок, текст и автор """
    mocker.patch("app.posts_list", return_value=posts_list)

    response = client.get('/posts/0')
    assert response.status_code == 200
    assert "Заголовок поста" in response.text
    assert "Текст поста" in response.text
    assert "Иванов Иван Иванович" in response.text


def test_post_not_found(client):
    """ Проверяет, что для несуществующего поста возвращается ошибка 404 """
    response = client.get("/posts/999")
    assert response.status_code == 404
    assert "404 Not Found" in response.text


def test_post_date_format(client, mocker, posts_list):
    """ Проверяет, что дата публикации поста отображается в правильном формате """
    mocker.patch("app.posts_list", return_value=posts_list)

    response = client.get('/posts/0')
    assert "10.03.2025" in response.text


def test_post_image(client, mocker, posts_list):
    """ Проверяет, что изображение поста корректно отображается на странице """
    mocker.patch("app.posts_list", return_value=posts_list)

    response = client.get('/posts/0')
    assert '123.jpg' in response.text


def test_index_template(client, captured_templates):
    """ Проверяет, что на главной странице используется шаблон 'index.html' """
    with captured_templates as templates:
        response = client.get('/')
        assert response.status_code == 200
        assert len(templates) == 1
        template, _ = templates[0]
        assert template.name == 'index.html'


def test_about_template(client, captured_templates):
    """ Проверяет, что на странице 'Об авторе' используется шаблон 'about.html' """
    with captured_templates as templates:
        response = client.get('/about')
        assert response.status_code == 200
        assert len(templates) == 1
        template, _ = templates[0]
        assert template.name == 'about.html'


def test_about_page_content(client):
    """ Проверяет, что на странице 'Об авторе' есть заголовок 'Об авторе' """
    response = client.get('/about')
    assert response.status_code == 200
    assert "Об авторе" in response.text


def test_posts_list_template(client, captured_templates, mocker, posts_list):
    """ Проверяет, что список постов рендерится с использованием шаблона 'posts.html' """
    with captured_templates as templates:
        mocker.patch("app.posts_list", return_value=posts_list)

        response = client.get('/posts')
        assert response.status_code == 200
        assert len(templates) == 1
        template, context = templates[0]
        assert template.name == 'posts.html'


def test_post_template(client, captured_templates, mocker, posts_list):
    """ Проверяет, что отдельный пост рендерится с использованием шаблона 'post.html' """
    with captured_templates as templates:
        mocker.patch("app.posts_list", return_value=posts_list)

        response = client.get('/posts/0')
        assert response.status_code == 200
        assert len(templates) == 1
        template, context = templates[0]
        assert template.name == 'post.html'


def test_posts_list_context(client, captured_templates, mocker, posts_list):
    """ Проверяет, что в шаблон списка постов передаются правильные данные """
    with captured_templates as templates:
        mocker.patch("app.posts_list", return_value=posts_list)

        response = client.get('/posts')
        assert response.status_code == 200
        assert len(templates) == 1
        _, context = templates[0]

        assert 'title' in context
        assert 'posts' in context
        assert context['title'] == 'Посты'
        assert len(context['posts']) == len(posts_list)


def test_comments_content(client, mocker, posts_list):
    """ Проверяет, что на странице поста отображаются комментарии пользователей """
    mocker.patch("app.posts_list", return_value=posts_list)

    response = client.get('/posts/0')
    assert response.status_code == 200
    assert "Пользователь 1" in response.text
    assert "Отличный пост!" in response.text


def test_comments_section_exists(client, mocker, posts_list):
    """ Проверяет, что на странице поста есть секция для комментариев """
    mocker.patch("app.posts_list", return_value=posts_list)

    response = client.get('/posts/0')
    assert response.status_code == 200
    assert "Оставьте комментарий" in response.text
