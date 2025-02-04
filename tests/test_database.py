# python -m unittest tests/test_update_database.py
import unittest
from unittest.mock import patch, MagicMock
import logging

# Assuming the functions are in a module named `db_script.py`
from database.database import get_db_connection, execute_schema


class TestDatabaseFunctions(unittest.TestCase):

    @patch('psycopg2.connect')
    def test_get_db_connection_success(self, mock_connect):
        """Test successful database connection."""
        mock_conn = MagicMock()
        mock_connect.return_value = mock_conn

        conn = get_db_connection()

        self.assertEqual(conn, mock_conn)
        mock_connect.assert_called_once()

        # Log success after test passes
        logging.info("Test passed for successful DB connection.")

    @patch('psycopg2.connect')
    def test_get_db_connection_failure(self, mock_connect):
        """Test failed database connection."""
        mock_connect.side_effect = Exception("Connection failed")

        conn = get_db_connection()

        self.assertIsNone(conn)
        mock_connect.assert_called_once()

        logging.info("Test passed for failed DB connection.")

@patch('psycopg2.connect')
@patch('os.path.exists')
@patch('builtins.open')
def test_execute_schema_success(self, mock_open, mock_exists, mock_connect):
    """Test successful schema execution."""
    mock_conn = MagicMock()
    mock_cursor = MagicMock()

    # Correctly return mock objects
    mock_connect.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor  # Ensure cursor is correctly mocked
    mock_exists.return_value = True
    mock_open.return_value.__enter__.return_value.read.return_value = "CREATE TABLE test (id INT);"

    result = execute_schema()

    self.assertTrue(result)
    mock_connect.assert_called_once()
    mock_cursor.execute.assert_called_once_with("CREATE TABLE test (id INT);")  # Should work now
    mock_conn.commit.assert_called_once()

    logging.info("Test passed for successful schema execution.")

    print(mock_cursor.mock_calls)  # Debugging: See what calls were made

    @patch('psycopg2.connect')
    @patch('os.path.exists')
    def test_execute_schema_file_not_found(self, mock_exists, mock_connect):
        """Test schema execution when file is not found."""
        mock_connect.return_value = MagicMock()
        mock_exists.return_value = False  # Simulate schema file missing

        result = execute_schema()

        self.assertFalse(result)  # Expecting failure because file doesn't exist
        logging.info("Test passed for schema file not found.")

    @patch('psycopg2.connect')
    @patch('os.path.exists')
    @patch('builtins.open')
    def test_execute_schema_failure(self, mock_open, mock_exists, mock_connect):
        """Test schema execution failure (e.g., database error)."""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_conn
        mock_exists.return_value = True
        mock_open.return_value.__enter__.return_value.read.return_value = "CREATE TABLE test (id INT);"
        mock_cursor.exe
