import pytest
from io import StringIO
import csv
from app.repositories import LogsRepository
from datetime import datetime


def test_log_creation(db_connector):
    repo = LogsRepository(db_connector)
    repo.create("/test-page", user_id=None)

    with db_connector.connect().cursor(named_tuple=True) as cursor:
        cursor.execute("SELECT * FROM visit_logs WHERE path = '/test-page'")
        log = cursor.fetchone()
        assert log is not None
        assert log.path == "/test-page"
        assert log.user_id is None

def test_get_all_logs(db_connector):
    repo = LogsRepository(db_connector)

    with db_connector.connect().cursor() as cursor:
        cursor.execute("DELETE FROM visit_logs")
        db_connector.connect().commit()

    repo.create("/page1", user_id=None)

    with db_connector.connect().cursor(named_tuple=True) as cursor:
        cursor.execute("SELECT * FROM visit_logs ORDER BY created_at DESC")
        logs = cursor.fetchall()
        assert len(logs) == 1
        assert logs[0].path == "/page1"


def test_page_stats_report(db_connector):
    repo = LogsRepository(db_connector)

    with db_connector.connect().cursor() as cursor:
        cursor.execute("DELETE FROM visit_logs")
        db_connector.connect().commit()

    repo.create("/home", user_id=None)
    repo.create("/about", user_id=None)
    repo.create("/home", user_id=None)
    repo.create("/contact", user_id=None)
    repo.create("/home", user_id=None)

    stats = repo.get_page_stats()

    assert len(stats) == 3

    # home_stats = None
    # for s in stats:
    #     if s.path == "/home":
    #         home_stats = s
    #         break

    home_stat = next((s for s in stats if s.path == "/home"), None)
    about_stat = next((s for s in stats if s.path == "/about"), None)
    contact_stat = next((s for s in stats if s.path == "/contact"), None)

    assert home_stat is not None
    assert home_stat.visit_count == 3

    assert about_stat is not None
    assert about_stat.visit_count == 1

    assert contact_stat is not None
    assert contact_stat.visit_count == 1

    assert stats[0].path == "/home"
    assert stats[0].visit_count == 3
    assert stats[1].visit_count == 1
    assert stats[2].visit_count == 1