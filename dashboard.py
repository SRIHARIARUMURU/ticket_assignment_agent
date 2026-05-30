import streamlit as st
import pandas as pd
import sqlite3
import os
from datetime import datetime
from streamlit_autorefresh import st_autorefresh

# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="AI Ticket Routing Platform",
    page_icon="🤖",
    layout="wide"
)

# =========================================================
# CUSTOM CSS
# =========================================================

st.markdown("""
<style>

.main {
    background-color: #0E1117;
    color: white;
}

.stApp {
    background-color: #0E1117;
}

h1, h2, h3, h4 {
    color: white;
}

[data-testid="stMetric"] {
    background-color: #1c1f26;
    border: 1px solid #2d3139;
    padding: 15px;
    border-radius: 12px;
}

[data-testid="stDataFrame"] {
    border-radius: 10px;
}

</style>
""", unsafe_allow_html=True)

# =========================================================
# DATABASE SETUP
# =========================================================

os.makedirs("database", exist_ok=True)

DB_PATH = os.path.join(
    "database",
    "tickets.db"
)

# =========================================================
# DATABASE CONNECTION
# =========================================================

def get_connection():

    return sqlite3.connect(
        DB_PATH,
        check_same_thread=False
    )

# =========================================================
# CREATE TABLES
# =========================================================

connection = get_connection()

cursor = connection.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS processed_tickets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ticket_number TEXT UNIQUE,
    short_description TEXT,
    assignment_group TEXT,
    assigned_engineer TEXT,
    priority TEXT,
    status TEXT,
    processed_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")

connection.commit()

connection.close()

# =========================================================
# AUTO REFRESH
# =========================================================

st_autorefresh(
    interval=5000,
    key="dashboard_refresh"
)

# =========================================================
# HEADER
# =========================================================

st.title("🤖 AI-Powered Ticket Routing Platform")

st.subheader(
    "Enterprise Agentic AI Operations Dashboard"
)

st.markdown("---")

# =========================================================
# FETCH METRICS
# =========================================================

metric_connection = get_connection()

metric_cursor = metric_connection.cursor()

# Processed Tickets
metric_cursor.execute("""
SELECT COUNT(*)
FROM processed_tickets
""")

processed_count = (
    metric_cursor.fetchone()[0]
)

# Active Engineers
metric_cursor.execute("""
SELECT COUNT(DISTINCT assigned_engineer)
FROM processed_tickets
WHERE assigned_engineer IS NOT NULL
AND assigned_engineer != 'Unassigned'
""")

active_engineers = (
    metric_cursor.fetchone()[0]
)

# Escalated Tickets
metric_cursor.execute("""
SELECT COUNT(*)
FROM processed_tickets
WHERE status='Escalated'
""")

escalated_count = (
    metric_cursor.fetchone()[0]
)

# Pending Tickets
metric_cursor.execute("""
SELECT COUNT(*)
FROM processed_tickets
WHERE status='Pending'
""")

pending_count = (
    metric_cursor.fetchone()[0]
)

metric_connection.close()

# =========================================================
# METRICS SECTION
# =========================================================

st.header("📊 System Metrics")

col1, col2, col3, col4 = st.columns(4)

with col1:

    st.metric(
        label="Processed Tickets",
        value=processed_count
    )

with col2:

    st.metric(
        label="Active Engineers",
        value=active_engineers
    )

with col3:

    st.metric(
        label="Escalated Tickets",
        value=escalated_count
    )

with col4:

    st.metric(
        label="Pending Tickets",
        value=pending_count
    )

st.markdown("---")

# =========================================================
# FETCH PROCESSED TICKETS
# =========================================================

data_connection = get_connection()

processed_df = pd.read_sql_query("""

SELECT
    ticket_number,
    short_description,
    assignment_group,
    assigned_engineer,
    priority,
    status,
    processed_time

FROM processed_tickets

ORDER BY processed_time DESC

""", data_connection)

data_connection.close()

# =========================================================
# SEARCH FILTER
# =========================================================

st.header("🔍 Search Tickets")

search_query = st.text_input(
    "Search by Ticket Number"
)

if search_query:

    processed_df = processed_df[
        processed_df["ticket_number"]
        .astype(str)
        .str.contains(
            search_query,
            case=False
        )
    ]

# =========================================================
# PROCESSED TICKETS TABLE
# =========================================================

st.markdown("---")

st.header("🎫 Processed Tickets")

if not processed_df.empty:

    st.dataframe(
        processed_df,
        use_container_width=True
    )

else:

    st.warning(
        "No processed tickets available."
    )

# =========================================================
# INCOMING TICKETS
# =========================================================

st.markdown("---")

st.header("📥 Incoming Tickets")

try:

    incoming_df = pd.read_json(
        "data/mock_tickets.json"
    )

    st.dataframe(
        incoming_df,
        use_container_width=True
    )

except Exception as e:

    st.error(
        f"Error loading tickets: {e}"
    )

# =========================================================
# ANALYTICS
# =========================================================

st.markdown("---")

st.header("📈 Ticket Analytics")

if not processed_df.empty:

    # Priority Chart
    st.subheader(
        "Priority Distribution"
    )

    priority_counts = (
        processed_df["priority"]
        .value_counts()
    )

    st.bar_chart(priority_counts)

    # Status Chart
    st.subheader(
        "Status Distribution"
    )

    status_counts = (
        processed_df["status"]
        .value_counts()
    )

    st.bar_chart(status_counts)

    # Assignment Group Chart
    st.subheader(
        "Assignment Group Distribution"
    )

    group_counts = (
        processed_df["assignment_group"]
        .value_counts()
    )

    st.bar_chart(group_counts)

else:

    st.info(
        "No analytics data available."
    )

# =========================================================
# PLATFORM STATUS
# =========================================================

st.markdown("---")

st.header("🖥️ Platform Status")

status_col1, status_col2, status_col3 = (
    st.columns(3)
)

with status_col1:

    st.success(
        "✅ AI Routing Engine Active"
    )

with status_col2:

    st.success(
        "✅ SQLite Database Connected"
    )

with status_col3:

    st.success(
        "✅ Streamlit Dashboard Running"
    )

# =========================================================
# LIVE LOGS
# =========================================================

st.markdown("---")

st.header("📜 Recent Logs")

try:

    if os.path.exists("logs/app.log"):

        with open(
            "logs/app.log",
            "r"
        ) as file:

            logs = file.readlines()

        recent_logs = logs[-15:]

        st.text(
            "".join(recent_logs)
        )

    else:

        st.warning(
            "No log file found."
        )

except Exception as e:

    st.error(
        f"Unable to load logs: {e}"
    )

# =========================================================
# FOOTER
# =========================================================

st.markdown("---")

st.caption(
    f"Last Updated: "
    f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
)

