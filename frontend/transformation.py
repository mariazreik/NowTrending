import pandas as pd
import sys
import os

BASE_DIR = os.getcwd()  # Gets current working directory

sys.path.append(os.path.abspath(os.path.join(BASE_DIR, "..")))

from database.database import get_db_connection  # Now import should work


def transform_google_locations():
    '''This function retrieves the google_locations table and returns the cleaned version as a pandas dataframe.'''
    conn = get_db_connection()
    if conn:
        try:
            # query to select the whole table
            query = "SELECT * FROM student.google_locations"
            # my dataframe
            df = pd.read_sql(query, conn)
            df_transformed = df.drop(['success', 'message', 'lastupdate', 'scrapedat'], axis=1)
            df_transformed['country'] = df_transformed['country'].str.lower()
            # original_length = len(df_transformed)
            df_unique = df_transformed.drop_duplicates(subset=['country'])
            # new_length = len(df_unique)
            # removed_count = original_length - new_length
            # print(f"Number of duplicate rows removed: {removed_count} out of {original_length}")
            # print(df_unique)
            return df_unique
        except Exception as e:
            print(f"An error occurred: {e}")
        finally:
            # always close connection when done
            conn.close()
    else:
        print("Failed to establish a database connection.")


def transform_google_trend():
    conn = get_db_connection()
    if conn:
        try:
            # my query
            query = "SELECT * FROM student.google_trend"
            # my dataframe
            df = pd.read_sql(query, conn)
            # drops duplicate rows
            df_unique = df.drop_duplicates()
            df_unique.rename(columns={'keyword': 'trend'}, inplace=True)
            df_unique['trend'] = df_unique['trend'].str.title()
            
            # print(df_unique.head())
            
            return(df_unique)
        except Exception as e:
            print(f"An error occurred: {e}")
        finally:
            # always close connection when done
            conn.close()
    else:
        print("Failed to establish a database connection.")


def transform_twitter_hashflags():
    # get the database connection
    conn = get_db_connection()
    if conn:
        try:
            # my query
            query = "SELECT * FROM student.twitter_hashflags"
            # my dataframe
            df = pd.read_sql(query, conn)
            df_unique = df.drop_duplicates()
            df_unique = df_unique.drop(['is_hashfetti_enabled'], axis=1)
            df_unique.rename(columns={'starting_timestamp_ms':'starting_timestamp', 'ending_timestamp_ms': 'ending_timestamp', 'asset_url': 'url'}, inplace=True)
            # prints the head
            # print(df_unique.head())
            return df_unique
        except Exception as e:
            print(f"An error occurred: {e}")
        finally:
            # always close connection when done
            conn.close()
    else:
        print("Failed to establish a database connection.")


def transform_twitter_trend():
    # get the database connection
    conn = get_db_connection()
    if conn:
        try:
            # my query
            query = "SELECT * FROM student.twitter_trend"
            # my dataframe
            df = pd.read_sql(query, conn)
            df['related_terms'] = df['related_terms'].astype(str)
            df_unique = df.drop_duplicates()
            df_unique.rename(columns={'trend_name' : 'trend'}, inplace=True)
            df_unique = df_unique.drop(['related_terms', 'impression_id'], axis=1)
            df_unique['domain_context'] = df['domain_context'].str.replace(r' . Trending$', '', regex=True)
            # prints the head
            # print(df_unique.head())
            return df_unique
        except Exception as e:
            print(f"An error occurred: {e}")
        finally:
            # always close connection when done
            conn.close()
    else:
        print("Failed to establish a database connection.")


def transform_twitter_locations():
    conn = get_db_connection()
    if conn:
        try:
            # my query
            query = "SELECT * FROM student.twitter_locations"
            # my dataframe
            df_unique = pd.read_sql(query, conn)
            df_unique['country_name'] = df['country_name'].str.lower()
            # original_length = len(df_unique)
            df_unique = df_unique.drop_duplicates(subset=['country_name'])
            df_unique.rename(columns={'country_name':'country'}, inplace=True)
            # new_length = len(df_unique)
            # removed_count = original_length - new_length
            # print(f"Number of duplicate rows removed: {removed_count} out of {original_length}")
            return df_unique
            # print(df_unique)
        except Exception as e:
            print(f"An error occurred: {e}")
        finally:
            # always close connection when done
            conn.close()
    else:
        print("Failed to establish a database connection.")