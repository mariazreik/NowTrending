import sys
import os
import logging
import json
import requests
from contextlib import closing
from datetime import datetime

# Extend sys path to access the database module
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from database.database import get_db_connection
from scripts.fetch_twitter_data import fetch_twitter_hashtags, fetch_twitter_trends, fetch_twitter_locations
from scripts.fetch_google_data import fetch_google_trends

# Set up basic logging configuration to suppress all logs except critical errors
logging.basicConfig(level=logging.CRITICAL)  # Only shows critical errors

GOOGLE_API_URL = "https://google-realtime-trends-data-api.p.rapidapi.com/trends"


def update_google_trends_database(google_data):
    """Update the Google trends data in the database, storing keywords separately."""
    if not google_data:
        logging.warning("No Google Trends data to update.")
        return

    try:
        records = google_data.get("data", []) if isinstance(google_data, dict) else google_data

        with get_db_connection() as conn:
            with closing(conn.cursor()) as cursor:
                # Query to insert into google_locations table
                trend_query = """
                    INSERT INTO student.google_locations (success, message, country, lastUpdate, scrapedAt)
                    VALUES (%s, %s, %s, %s, %s)
                    RETURNING id;
                """
                
                # Query to insert keywords into google_trend table
                keyword_query = """
                    INSERT INTO student.google_trend (google_location_id, keyword)
                    VALUES (%s, %s);
                """

                for record in records:
                    success = True
                    message = "OK"
                    country = record.get("country")
                    keywords = record.get("keywordsText", [])  # List of keywords
                    
                    lastUpdate_str = record.get("lastUpdate", "")
                    scrapedAt_str = record.get("scrapedAt", "")

                    lastUpdate_dt = datetime.strptime(lastUpdate_str, "%d-%m-%Y , %H:%M:%S") if lastUpdate_str else None
                    scrapedAt_dt = datetime.fromisoformat(scrapedAt_str.replace("Z", "+00:00")) if scrapedAt_str else None

                    # Insert main trend entry and get its ID
                    cursor.execute(trend_query, (success, message, country, lastUpdate_dt, scrapedAt_dt))
                    trend_id = cursor.fetchone()[0]

                    # Insert each keyword separately
                    for keyword in keywords:
                        cursor.execute(keyword_query, (trend_id, keyword))

                conn.commit()

    except Exception as e:
        logging.error(f"Error updating Google Trends database: {e}")


def update_hashflags_database():
    """Fetch and update hashflags data in the database."""
    hashtags = fetch_twitter_hashtags()  # Fetch the latest hashtags

    if not hashtags:
        logging.warning("No hashtags found to update.")
        return

    try:
        with get_db_connection() as conn:
            with closing(conn.cursor()) as cursor:  # Automatically closes cursor after usage
                for tag in hashtags:
                    hashtag = tag["hashtag"]
                    starting_timestamp_ms = tag["starting_timestamp_ms"] / 1000  # Convert ms → seconds
                    ending_timestamp_ms = tag["ending_timestamp_ms"] / 1000
                    asset_url = tag.get("asset_url", None)
                    is_hashfetti_enabled = tag.get("is_hashfetti_enabled", False)

                    query = """
                    INSERT INTO student.twitter_hashflags (hashtag, starting_timestamp_ms, ending_timestamp_ms, asset_url, is_hashfetti_enabled)
                    VALUES (%s, to_timestamp(%s), to_timestamp(%s), %s, %s)
                    ON CONFLICT (hashtag)
                    DO UPDATE SET
                        starting_timestamp_ms = EXCLUDED.starting_timestamp_ms,
                        ending_timestamp_ms = EXCLUDED.ending_timestamp_ms,
                        asset_url = EXCLUDED.asset_url,
                        is_hashfetti_enabled = EXCLUDED.is_hashfetti_enabled,
                        last_updated = CURRENT_TIMESTAMP;
                    """

                    cursor.execute(query, (hashtag, starting_timestamp_ms, ending_timestamp_ms, asset_url, is_hashfetti_enabled))

                conn.commit()  # Commit the transaction after updating all hashflags

    except Exception as e:
        logging.error(f"Error updating hashflags database: {e}")


def update_twitter_locations(locations):
    """Insert only country-level locations into the database, ignoring invalid ones."""
    if not locations:
        logging.warning("No locations data to update.")
        return

    try:
        with get_db_connection() as conn:
            with closing(conn.cursor()) as cursor:
                query = """
                INSERT INTO student.twitter_locations (location_id, country_name)
                VALUES (%s, %s)
                ON CONFLICT (location_id) DO NOTHING;
                """

                location_data = []

                for loc in locations:
                    location_id = loc.get("place_id")
                    country_name = loc.get("name")
                    location_type = loc.get("location_type")

                    # Only insert if the location is a country
                    if location_id and country_name and location_type == "Country":
                        logging.info(f"Inserting country location: {location_id}, {country_name}")
                        location_data.append((location_id, country_name))
                    else:
                        # This specific error is handled silently.
                        if location_type != "Country":
                            logging.debug(f"Skipping invalid location data: {loc}")
                            continue

                if location_data:
                    logging.info(f"Inserting {len(location_data)} valid country locations into the database")
                    cursor.executemany(query, location_data)
                    conn.commit()

                else:
                    logging.warning("No valid country locations to insert")
                    
    except Exception as e:
        logging.error(f"Error updating Twitter locations database: {e}")


def update_trends_database(trends, location_id):
    """Update the Twitter trends data in the database, now with location_id."""
    try:
        with get_db_connection() as conn:
            with closing(conn.cursor()) as cursor:
                cursor.execute("SELECT trend_name FROM student.twitter_trend WHERE location_id = %s;", (location_id,))
                existing_trends = {row[0] for row in cursor.fetchall()}

                query = """
                INSERT INTO student.twitter_trend (trend_name, position, meta_description, domain_context, url, impression_id, related_terms, location_id)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (trend_name, location_id) DO NOTHING;
                """  # Avoid duplicate trends per location

                new_trends = []

                for trend in trends:
                    trend_name = trend.get("trendName")
                    if trend_name in existing_trends:
                        continue

                    position = trend.get("position", 0)
                    meta_description = trend.get("metaDescription", "")
                    domain_context = trend.get("domainContext", "")
                    url = trend.get("url", "")
                    impression_id = trend.get("impressionId", "")
                    related_terms = trend.get("relatedTerms", [])
                    related_terms = "{" + ",".join(f'"{term}"' for term in related_terms) + "}" if related_terms else "{}"

                    new_trends.append((trend_name, position, meta_description, domain_context, url, impression_id, related_terms, location_id))

                if new_trends:
                    cursor.executemany(query, new_trends)

                conn.commit()

    except Exception as e:
        logging.error(f"Error updating trends database: {e}")


def parse_trends_data(trends_data):
    """Parse the trends data returned from Twitter."""
    parsed_trends = []
    timeline_data = trends_data.get("timeline", {})
    instructions = timeline_data.get("instructions", [])

    entries = []
    for instruction in instructions:
        if "addEntries" in instruction:
            entries = instruction["addEntries"].get("entries", [])
            break

    if not entries:
        return parsed_trends

    for entry in entries:
        content = entry.get("content", {})
        trend = content.get("timelineModule", {}).get("items", [])

        for item in trend:
            trend_data = item.get("item", {}).get("content", {}).get("trend", {})

            if trend_data:
                parsed_trends.append({
                    "trendName": trend_data.get("name"),
                    "position": item.get("item", {}).get("clientEventInfo", {}).get("details", {}).get("guideDetails", {}).get("transparentGuideDetails", {}).get("trendMetadata", {}).get("position", 0),
                    "metaDescription": trend_data.get("trendMetadata", {}).get("metaDescription", ""),
                    "domainContext": trend_data.get("trendMetadata", {}).get("domainContext", ""),
                    "url": trend_data.get("url", {}).get("url", ""),
                    "impressionId": trend_data.get("clientEventInfo", {}).get("details", {}).get("guideDetails", {}).get("transparentGuideDetails", {}).get("trendMetadata", {}).get("impressionId", ""),
                    "relatedTerms": trend_data.get("clientEventInfo", {}).get("details", {}).get("guideDetails", {}).get("transparentGuideDetails", {}).get("trendMetadata", {}).get("relatedTerms", [])
                })

    return parsed_trends


def main():
    """Main function to update locations, Twitter trends, and Google trends data."""
    
    # Fetch and update Twitter locations
    locations = fetch_twitter_locations()
    if locations:
        update_twitter_locations(locations)
    else:
        logging.error("Failed to fetch Twitter locations.")

    # Fetch and update Twitter trends per location
    if locations:
        for location in locations:
            location_id = location.get("place_id")
            if not location_id:
                continue
            
            trends_data = fetch_twitter_trends(location_id)
            if isinstance(trends_data, dict):
                parsed_trends = parse_trends_data(trends_data)
                if parsed_trends:
                    update_trends_database(parsed_trends, location_id)
    
    # Fetch and update Google trends
    google_data = fetch_google_trends()
    if google_data:
        update_google_trends_database(google_data)
    else:
        logging.error("Failed to fetch or update Google Trends data.")

if __name__ == "__main__":
    main()
