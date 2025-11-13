from app.repositories import LogsRepository
import pytest


@pytest.fixture(autouse=True)
def clean_logs(db_connector):
    with db_connector.connect().cursor() as cursor:
        cursor.execute("DELETE FROM visit_logs;")
        cursor.execute("ALTER TABLE visit_logs AUTO_INCREMENT = 1;")
        db_connector.connect().commit()


def test_create_log(db_connector):
    repo = LogsRepository(db_connector)

    repo.create("/test-page", user_id=None)

    with db_connector.connect().cursor(named_tuple=True) as cursor:
        cursor.execute("SELECT * FROM visit_logs WHERE path = '/test-page';")
        log = cursor.fetchone()
        assert log is not None
        assert log.path == "/test-page"
        assert log.user_id is None


def test_get_paginated_logs(db_connector):
    repo = LogsRepository(db_connector)

    for i in range(25):
        repo.create(f"/page-{i}", user_id=None)

    pagination = repo.get_paginated(page=2, per_page=10, user_id=None)

    assert pagination.total == 25
    assert pagination.per_page == 10
    assert pagination.page == 2
    assert len(pagination.items) == 10


def test_get_page_stats(db_connector):
    repo = LogsRepository(db_connector)

    repo.create("/home", user_id=None)
    repo.create("/home", user_id=None)
    repo.create("/about", user_id=None)

    stats = repo.get_page_stats()

    home_stats = next((s for s in stats if s.path == "/home"), None)
    about_stats = next((s for s in stats if s.path == "/about"), None)

    assert home_stats is not None
    assert home_stats.visit_count == 2
    assert about_stats is not None
    assert about_stats.visit_count == 1