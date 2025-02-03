import unittest
from unittest.mock import patch

# Assuming your code is in a file called twitter_api.py
from scripts.fetch_twitter_data import fetch_twitter_locations, fetch_twitter_hashtags, fetch_twitter_trends


class TestTwitterAPI(unittest.TestCase):

    @patch('requests.get')
    def test_fetch_twitter_locations_success(self, mock_get):
        # Simulate a successful API response
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = [{"place_id": "123", "name": "Test Location"}]

        result = fetch_twitter_locations()
        self.assertIsNotNone(result)
        self.assertEqual(result[0]['place_id'], "123")
        self.assertEqual(result[0]['name'], "Test Location")

    @patch('requests.get')
    def test_fetch_twitter_locations_failure(self, mock_get):
        # Simulate an API failure
        mock_get.return_value.status_code = 500
        mock_get.return_value.text = "Internal Server Error"

        result = fetch_twitter_locations()
        self.assertIsNone(result)

    @patch('requests.get')
    def test_fetch_twitter_hashtags_success(self, mock_get):
        # Simulate a successful API response
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {"hashtags": ["#Python", "#Coding"]}

        result = fetch_twitter_hashtags()
        self.assertIsNotNone(result)
        self.assertIn("#Python", result['hashtags'])
        self.assertIn("#Coding", result['hashtags'])

    @patch('requests.get')
    def test_fetch_twitter_trends_success(self, mock_get):
        # Simulate a successful API response
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {"trends": ["#PythonTrending", "#TechNews"]}

        result = fetch_twitter_trends("123")
        self.assertIsNotNone(result)
        self.assertIn("#PythonTrending", result['trends'])
        self.assertIn("#TechNews", result['trends'])


if __name__ == '__main__':
    unittest.main()
