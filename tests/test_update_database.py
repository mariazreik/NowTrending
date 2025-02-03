import unittest
from unittest.mock import patch, MagicMock
from scripts.update_database import update_hashflags_database, update_trends_database


class TestTwitterDataUpdate(unittest.TestCase):

    @patch('scripts.fetch_twitter_data.fetch_twitter_hashtags')
    @patch('scripts.fetch_twitter_data.fetch_twitter_trends')
    @patch('database.database.get_db_connection')
    def test_update_hashflags_database(self, mock_get_db_connection, mock_fetch_trends, mock_fetch_hashtags):
        # Mock the fetch_twitter_hashtags response
        mock_fetch_hashtags.return_value = [{"hashtag": "#Test", "starting_timestamp_ms": 1609459200000, "ending_timestamp_ms": 1609545600000}]
        
        # Mock the database connection
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_db_connection.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        
        # Run the function
        update_hashflags_database()
        
        # Assertions
        mock_cursor.execute.assert_called_once_with(  # Check that the correct query was executed
            'INSERT INTO student.twitter_hashflags (hashtag, starting_timestamp_ms, ending_timestamp_ms, asset_url, is_hashfetti_enabled) VALUES (%s, to_timestamp(%s), to_timestamp(%s), %s, %s) ON CONFLICT (hashtag) DO UPDATE SET starting_timestamp_ms = EXCLUDED.starting_timestamp_ms, ending_timestamp_ms = EXCLUDED.ending_timestamp_ms, asset_url = EXCLUDED.asset_url, is_hashfetti_enabled = EXCLUDED.is_hashfetti_enabled, last_updated = CURRENT_TIMESTAMP;',
            ('#Test', 1609459200, 1609545600, None, False)
        )
        
        mock_conn.commit.assert_called_once()  # Ensure that commit was called

    @patch('scripts.fetch_twitter_data.fetch_twitter_hashtags')
    @patch('scripts.fetch_twitter_data.fetch_twitter_trends')
    @patch('database.database.get_db_connection')
    def test_update_trends_database(self, mock_get_db_connection, mock_fetch_trends, mock_fetch_hashtags):
        # Test data
        trends_data = [
            {
                "trendName": "#Python",
                "position": 1,
                "metaDescription": "A programming language",
                "domainContext": "Technology",
                "url": "https://www.example.com",
                "impressionId": "12345",
                "relatedTerms": ["programming", "coding"]
            },
            {
                "trendName": "#JavaScript",
                "position": 2,
                "metaDescription": "Another programming language",
                "domainContext": "Technology",
                "url": "https://www.example2.com",
                "impressionId": "67890",
                "relatedTerms": ["programming", "web"]
            }
        ]
        
        # Mock the fetch_twitter_trends response
        mock_fetch_trends.return_value = {
            "timeline": {
                "instructions": [
                    {
                        "addEntries": {
                            "entries": [
                                {
                                    "content": {
                                        "timelineModule": {
                                            "items": [
                                                {
                                                    "item": {
                                                        "content": {
                                                            "trend": trends_data[0]  # Using actual test data
                                                        }
                                                    }
                                                },
                                                {
                                                    "item": {
                                                        "content": {
                                                            "trend": trends_data[1]  # Using actual test data
                                                        }
                                                    }
                                                }
                                            ]
                                        }
                                    }
                                }
                            ]
                        }
                    }
                ]
            }
        }

        # Mock the database connection
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_db_connection.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        # Simulate existing trends in the database
        mock_cursor.execute.return_value = None  # No actual database call
        mock_cursor.fetchall.return_value = [("#Python")]  # Simulate #Python already existing in the database

        # Call the update_trends_database function
        update_trends_database(trends_data)

        # Assert that only one trend (#JavaScript) was inserted and #Python was skipped
        mock_cursor.executemany.assert_called_once_with(
            """
            INSERT INTO student.twitter_trends (trend_name, position, meta_description, domain_context, url, impression_id, related_terms)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (trend_name) DO NOTHING;
            """, [
                ('#JavaScript', 2, "Another programming language", "Technology", "https://www.example2.com", "67890", '{"programming", "web"}')
            ])

        # Ensure that commit was called to save changes
        mock_conn.commit.assert_called_once()

    @patch('database.database.get_db_connection')
    def test_update_trends_database_empty(self, mock_get_db_connection):
        # Test that the function does nothing if no trends data is provided
        update_trends_database([])  # Empty data list

        # Assert that commit was not called, because there is no data to insert
        mock_get_db_connection().commit.assert_not_called()


if __name__ == '__main__':
    unittest.main()
