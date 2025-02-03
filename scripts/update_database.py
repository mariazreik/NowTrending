import sys
import os
import logging
from contextlib import closing

# Extend sys path to access the database module
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from database.database import get_db_connection
from scripts.fetch_twitter_data import fetch_twitter_hashtags, fetch_twitter_trends

# Set up basic logging configuration
logging.basicConfig(level=logging.INFO)


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


def update_trends_database(trends):
    """Update the trends data in the database."""
    try:
        with get_db_connection() as conn:
            with closing(conn.cursor()) as cursor:
                cursor.execute("SELECT trend_name FROM student.twitter_trends;")
                existing_trends = {row[0] for row in cursor.fetchall()}

                query = """
                    INSERT INTO student.twitter_trends (trend_name, position, meta_description, domain_context, url, impression_id, related_terms)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (trend_name) DO NOTHING;
                """

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

                    new_trends.append((trend_name, position, meta_description, domain_context, url, impression_id, related_terms))

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
    """Main function to update hashflags and trends data."""
    update_hashflags_database()
    
    location_id = -7608764736147602991  # Location ID for the Twitter trends
    trends_data = fetch_twitter_trends(location_id)

    if not isinstance(trends_data, dict):
        logging.error("Invalid data format received from Twitter API.")
        return

    parsed_trends = parse_trends_data(trends_data)

    if parsed_trends:
        update_trends_database(parsed_trends)


if __name__ == "__main__":
    main()
