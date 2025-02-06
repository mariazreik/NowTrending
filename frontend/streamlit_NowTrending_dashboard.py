import streamlit as st
import pandas as pd
import os
import sys
import base64
import subprocess

# Add the parent directory of 'frontend' to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from frontend.explorations import twitter_data, top5_per_context

def refresh_data():
    """Runs the script to update the database."""
    script_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "scripts", "update_database.py"))
    with st.spinner("Refreshing data..."):
        result = subprocess.run([sys.executable, script_path], capture_output=True, text=True)
        if result.returncode == 0:
            st.success("Data refreshed successfully!")
        else:
            st.error(f"Failed to refresh data: {result.stderr}")


def set_background(image_file):
    """Sets the background image for the app."""
    with open(image_file, "rb") as f:
        encoded_string = base64.b64encode(f.read()).decode()
    css = f"""
    <style>
    .stApp {{
        background-image: url("data:image/png;base64,{encoded_string}");
        background-size: cover;
    }}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)

def set_sidebar_image(image_file):
    """Sets the sidebar image dynamically."""
    with open(image_file, "rb") as f:
        encoded_string = base64.b64encode(f.read()).decode()
    st.sidebar.markdown(
        f"""
        <style>
        .sidebar-img {{
            display: block;
            margin-left: auto;
            margin-right: auto;
            width: 100%;
            border-radius: 10px;
        }}
        </style>
        <img class="sidebar-img" src="data:image/png;base64,{encoded_string}" />
        """,
        unsafe_allow_html=True
    )

st.markdown(
    """
    <style>
    /* Adjusting the main content area */
    .main .block-container {
        max-width: 70%; /* Reduce the width to create a shift */
        margin-left: -10%;
        margin-right: 15%; /* Shift towards the sidebar */
    }
    </style>
    """,
    unsafe_allow_html=True
)


# Set the background image
set_background("lightmode.jpg")

# Add a sidebar with a title and options
platform = st.sidebar.selectbox(
    "Platforms:",
    ("Twitter", "Google")
)

# Set different sidebar images based on the platform selection
if platform == "Twitter":
    set_sidebar_image("twitter.png")  # Replace with the actual image path
elif platform == "Google":
    set_sidebar_image("Google-Logo.png")  # Replace with the actual image path


# Inject custom CSS to change selectbox options to blue
st.markdown(
    """
    <style>
    div[data-baseweb="select"] > div {
        background-color: #1DA1F2;  /* Twitter blue background */
        color: white;  /* White text */
    }
    div[data-baseweb="select"] > div:hover {
        background-color: #0d8ddb;  /* Darker blue on hover */
    }
    </style>
    """,
    unsafe_allow_html=True
)


def parse_popularity(pop_str):
    """
    Convert a popularity string with 'K' or 'M' suffixes to a numeric value.
    e.g. '1.7M' becomes 1700000, '997K' becomes 997000, and plain numbers are converted to float.
    """
    pop_str = pop_str.strip()
    if pop_str.endswith("M"):
        try:
            return float(pop_str[:-1]) * 1_000_000
        except ValueError:
            return 0
    elif pop_str.endswith("K"):
        try:
            return float(pop_str[:-1]) * 1_000
        except ValueError:
            return 0
    else:
        try:
            return float(pop_str)
        except ValueError:
            return 0

if platform == "Twitter":
    st.subheader("The Hottest Twitter Trends")
    with st.expander("Description"):
        st.write("""
            This section displays the Top 10 trends on Twitter at the moment. It also gives you an option to find the Top 10 trends by Country, Category or both!
        """)

    df_top_ten = twitter_data()

    # Convert country names to title case so that options appear properly
    df_top_ten['country'] = df_top_ten['country'].str.title()

    # Get unique countries (sorted alphabetically) and domain contexts
    countries = sorted(df_top_ten['country'].unique().tolist())
    domain_contexts = df_top_ten['domain_context'].unique().tolist()

    # Multiselect widgets for country and domain context
    selected_countries = st.multiselect('Select Country:', ['All'] + countries, default='All')
    selected_domains = st.multiselect('Select Category:', ['All'] + domain_contexts, default='All')

    # Filter the DataFrame based on selections
    if 'All' not in selected_countries:
        df_top_ten = df_top_ten[df_top_ten['country'].isin(selected_countries)]
    if 'All' not in selected_domains:
        df_top_ten = df_top_ten[df_top_ten['domain_context'].isin(selected_domains)]

    # Select only 'Trend', 'Popularity', and 'URL' columns and keep the top 10 rows
    df_top_ten = df_top_ten[['Trend', 'Popularity', 'URL']].head(10)
    
    # Format the 'Trend' column to title case
    df_top_ten['Trend'] = df_top_ten['Trend'].str.title()

    # Create a numeric column for sorting based on the 'Popularity' string
    df_top_ten['Popularity_numeric'] = df_top_ten['Popularity'].apply(parse_popularity)
    
    # Sort the table by the numeric popularity in descending order
    df_top_ten = df_top_ten.sort_values(by='Popularity_numeric', ascending=False)
    
    # Remove the numeric column since it is not needed for display
    df_top_ten = df_top_ten.drop(columns=['Popularity_numeric'])
    
    # Create clickable links in the 'Trend' column by wrapping the text with an HTML <a> tag
    df_top_ten['Trend'] = df_top_ten.apply(
        lambda row: f'<a href="{row["URL"]}" target="_blank">{row["Trend"]}</a>', axis=1
    )
    
    # Enhanced CSS for a more aesthetic, blue-themed table
    st.markdown(
        """
        <style>
        /* Table Container */
        .custom-table {
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
            border-radius: 8px;
            overflow: hidden;
        }
        /* Table Header */
        .custom-table thead {
            background-color: #1DA1F2;
        }
        .custom-table thead th {
            color: #ffffff;
            padding: 15px;
            text-align: left;
            font-weight: bold;
            font-size: 16px;
        }
        /* Table Body */
        .custom-table tbody td {
            padding: 12px 15px;
            border-bottom: 1px solid #f0f0f0;
        }
        .custom-table tbody tr:nth-child(odd) {
            background-color: #E1F5FE;
        }
        .custom-table tbody tr:nth-child(even) {
            background-color: #B3E5FC;
        }
        .custom-table tbody tr:hover {
            background-color: #81D4FA;
            transition: background-color 0.3s ease;
        }
        /* Links in table cells */
        .custom-table tbody td a {
            color: #1DA1F2;
            text-decoration: none;
            font-weight: 500;
        }
        .custom-table tbody td a:hover {
            text-decoration: underline;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    # Convert DataFrame to HTML table with custom class and remove index
    table_html = df_top_ten[['Trend', 'Popularity']].to_html(
        escape=False, index=False, classes="custom-table"
    )
    st.markdown(table_html, unsafe_allow_html=True)

    # --------------------------------------------------
    # NEW SECTION: The Latest Trends (by domain_context)
    # --------------------------------------------------
    st.subheader("The Latest Twitter Trends")
    with st.expander("Description"):
        st.write("""
            This section displays the Latest 5 trends on Twitter. It also gives you an option to see the Latest 5 in each category.
        """)
    
    # Retrieve the latest trends DataFrame from your function
    df_sorted = top5_per_context()
    df_sorted = df_sorted.sort_values('last_updated', ascending=False)
    
    # Create a selectbox for domain_context filtering
    domain_context_options = sorted(df_sorted['Category'].unique())
    selected_domain_for_latest = st.selectbox(
        "Select a Category for Latest Trends:",
        options=["All"] + domain_context_options
    )
    
    # Filter and select the top 5 based on the selection
    if selected_domain_for_latest == "All":
        # Display overall latest trends (top 5)
        latest_trends = df_sorted.head(5)
    else:
        # Filter by the selected domain and then show top 5
        latest_trends = (
            df_sorted[df_sorted['Category'] == selected_domain_for_latest]
            .sort_values('last_updated', ascending=False)
            .head(5)
        )
    
    # Create clickable links in the 'Trend' column.
    # This assumes that the DataFrame has an extra column named "url" containing the corresponding link.
    latest_trends['Trend'] = latest_trends.apply(
        lambda row: f'<a href="{row["url"]}" target="_blank">{row["Trend"]}</a>', axis=1
    )
    
    # Convert the DataFrame to an HTML table with the same custom CSS,
    # and output only the "Category" and "Trend" columns.
    table_html_latest = latest_trends[['Trend', 'Category']].to_html(
        escape=False, index=False, classes="custom-table"
    )
    st.markdown(table_html_latest, unsafe_allow_html=True)
    
elif platform == "Google":
    st.write("You selected Google.")

# Sidebar button to refresh data
st.sidebar.markdown("""---""")  # Adds a separator line
if st.sidebar.button("Refresh Data"):
    refresh_data()