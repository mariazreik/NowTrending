# this file reads the .env file and makes the variables accessible in Python
import os
from dotenv import load_dotenv
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# load environment variables
load_dotenv()

# Twitter API
TWITTER_API_KEY = os.getenv("TWITTER_API_KEY")
TWITTER_API_HOST = os.getenv("TWITTER_API_HOST")

TWITTER_HASHFLAGS_KEY = os.getenv("TWITTER_HASHFLAGS_KEY")
TWITTER_HASHFLAGS_HOST = os.getenv("TWITTER_HASHFLAGS_HOST")

# Google API
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
GOOGLE_API_HOST = os.getenv("GOOGLE_API_HOST")

# database config
DB_HOST = os.getenv("DB_HOST")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASS = os.getenv("DB_PASS")
DB_PORT = os.getenv("DB_PORT")
