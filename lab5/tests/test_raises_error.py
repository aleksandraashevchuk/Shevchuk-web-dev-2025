import pytest
from mysql.connector import IntegrityError, OperationalError, ProgrammingError, DatabaseError


def test_create_user_raises_integrity_error(user_repository, mocker):
    mock_cursor = mocker.MagicMock()
    mock_cursor.execute.side_effect = IntegrityError("Duplicate entry")

    mock_connection = mocker.MagicMock()
    mock_connection.cursor.return_value.__enter__.return_value = mock_cursor

    mocker.patch.object(user_repository.db_connector, "connect", return_value=mock_connection)

    with pytest.raises(IntegrityError):
        user_repository.create("testuser", "123456", "John", "", "Smith", 1)


def test_get_user_raises_operational_error(user_repository, mocker):
    mock_cursor = mocker.MagicMock()
    mock_cursor.execute.side_effect = OperationalError("Lost connection")

    mock_connection = mocker.MagicMock()
    mock_connection.cursor.return_value.__enter__.return_value = mock_cursor

    mocker.patch.object(user_repository.db_connector, "connect", return_value=mock_connection)

    with pytest.raises(OperationalError):
        user_repository.get_by_id(1)


def test_update_user_raises_programming_error(user_repository, mocker):
    mock_cursor = mocker.MagicMock()
    mock_cursor.execute.side_effect = ProgrammingError("Syntax error")

    mock_connection = mocker.MagicMock()
    mock_connection.cursor.return_value.__enter__.return_value = mock_cursor

    mocker.patch.object(user_repository.db_connector, "connect", return_value=mock_connection)

    with pytest.raises(ProgrammingError):
        user_repository.update(1, "New", "Middle", "Last", 1)


def test_delete_user_raises_database_error(user_repository, mocker):
    mock_cursor = mocker.MagicMock()
    mock_cursor.execute.side_effect = DatabaseError("General DB error")

    mock_connection = mocker.MagicMock()
    mock_connection.cursor.return_value.__enter__.return_value = mock_cursor

    mocker.patch.object(user_repository.db_connector, "connect", return_value=mock_connection)

    with pytest.raises(DatabaseError):
        user_repository.delete(1)