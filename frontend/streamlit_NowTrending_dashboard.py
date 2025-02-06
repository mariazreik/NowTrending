import streamlit as st
import pandas as pd
import os
import sys
import base64
import subprocess
import urllib.parse

# Add the parent directory of 'frontend' to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from frontend.explorations import twitter_data, top5_per_context, google_loc

def refresh_data():
    """Runs the script to update the database."""
    script_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "scripts", "update_database.py"))
    with st.spinner("Refreshing data..."):
        result = subprocess.run([sys.executable, script_path], capture_output=True, text=True)
        if result.returncode == 0:
            st.success("Data refreshed successfully!")
        else:
            st.error(f"Failed to refresh data: {result.stderr}")

def make_clickable_trend(trend):
    """Generate a clickable Twitter search URL for a given trend."""
    encoded_trend = urllib.parse.quote_plus(trend)
    return f'<a href="https://twitter.com/search?q={encoded_trend}&src=typed_query" target="_blank">{trend}</a>'

def parse_popularity(pop_str):
    """Convert a popularity string (e.g., '1.7M posts') to a numeric value."""
    pop_str = pop_str.strip().lower().replace(" posts", "")
    if pop_str.endswith("m"):
        return float(pop_str[:-1]) * 1_000_000
    elif pop_str.endswith("k"):
        return float(pop_str[:-1]) * 1_000
    else:
        return float(pop_str) if pop_str.isnumeric() else 0

st.title("Trending Topics Dashboard")

# Sidebar selection
platform = st.sidebar.selectbox("Platforms:", ("Twitter", "Google"))

if platform == "Twitter":
    st.subheader("The Hottest Twitter Trends")
    with st.expander("Description"):
        st.write("Displays the Top 10 trends on Twitter. Filter by Country or Category!")

    df_top_ten = twitter_data()
    df_top_ten['country'] = df_top_ten['country'].str.title()
    countries = sorted(df_top_ten['country'].unique().tolist())
    domain_contexts = df_top_ten['domain_context'].unique().tolist()

    selected_countries = st.multiselect('Select Country:', ['All'] + countries, default='All')
    selected_domains = st.multiselect('Select Category:', ['All'] + domain_contexts, default='All')

    if 'All' not in selected_countries:
        df_top_ten = df_top_ten[df_top_ten['country'].isin(selected_countries)]
    if 'All' not in selected_domains:
        df_top_ten = df_top_ten[df_top_ten['domain_context'].isin(selected_domains)]

    df_top_ten = df_top_ten[['Trend', 'Popularity']].head(10)
    df_top_ten['Trend'] = df_top_ten['Trend'].str.title()
    df_top_ten['Popularity_numeric'] = df_top_ten['Popularity'].apply(parse_popularity)
    df_top_ten = df_top_ten.sort_values(by='Popularity_numeric', ascending=False).drop(columns=['Popularity_numeric'])
    
    df_top_ten['Trend'] = df_top_ten['Trend'].apply(make_clickable_trend)
    
    for index, row in df_top_ten.iterrows():
        st.markdown(f"- [{row['Trend']}](https://twitter.com/search?q={urllib.parse.quote_plus(row['Trend'])}&src=typed_query)", unsafe_allow_html=True)


    st.subheader("The Latest Twitter Trends")
    with st.expander("Description"):
        st.write("Displays the Latest 5 trends on Twitter.")

    df_sorted = top5_per_context().sort_values('last_updated', ascending=False)
    domain_context_options = sorted(df_sorted['Category'].unique())
    selected_domain_for_latest = st.selectbox("Select a Category:", ["All"] + domain_context_options)

    if selected_domain_for_latest == "All":
        latest_trends = df_sorted.head(5)
    else:
        latest_trends = df_sorted[df_sorted['Category'] == selected_domain_for_latest].head(5)

    latest_trends['Trend'] = latest_trends['Trend'].apply(make_clickable_trend)
    
    st.markdown(latest_trends[['Trend', 'Category']].to_html(escape=False, index=False), unsafe_allow_html=True)

elif platform == "Google":
    st.subheader("The Latest Google Trends")
    with st.expander('Description'):
        st.write("Displays the Latest Google Trends and allows filtering by country.")

    df_google = google_loc()
    df_google['last_updated'] = pd.to_datetime(df_google['last_updated'])
    df_google['Country'] = df_google['Country'].str.title()
    country_options = sorted(df_google['Country'].unique())
    selected_country = st.selectbox("Filter by Country:", ["All"] + country_options)

    if selected_country != "All":
        df_filtered = df_google[df_google['Country'] == selected_country]
    else:
        df_filtered = df_google.copy()

    df_filtered = df_filtered.sort_values('last_updated', ascending=False).head(10)
    df_filtered['Trend'] = df_filtered['Trend'].str.title()
    df_filtered['Trend'] = df_filtered['Trend'].apply(lambda trend: f'<a href="https://www.google.com/search?q={urllib.parse.quote_plus(trend)}" target="_blank">{trend}</a>')
    
    st.markdown(df_filtered[['Trend']].to_html(escape=False, index=False), unsafe_allow_html=True)

st.sidebar.markdown("""---""")
if st.sidebar.button("Refresh Data"):
    refresh_data()
