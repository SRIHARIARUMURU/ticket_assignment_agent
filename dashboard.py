import streamlit as st
import pandas as pd
import sqlite3
import json
from datetime import datetime


# Page Config
st.set_page_config(

    page_title="AI Ticket Routing Platform",

    page_icon="🤖",

    layout="wide"

)


# Dashboard Title
st.title(
    "🤖 AI-Powered Ticket Routing Platform"
)

st.markdown(
    "Enterprise Agentic AI Operations Dashboard"
)


# Current Time
st.sidebar.write(
    f"Last Refresh: {datetime.now()}"
)


# Database Connection
os.makedirs("database", exist_ok=True)

DB_PATH = os.path.join("database", "tickets.db")

connection = sqlite3.connect(DB_PATH)

cursor = connection.cursor()





# Metrics Section
st.subheader("📊 System Metrics")

col1, col2, col3 = st.columns(3)

# Total Processed Tickets
cursor.execute(
    "SELECT COUNT(*) FROM processed_tickets"
)

total_tickets = cursor.fetchone()[0]

# Unique Engineers
cursor.execute(
    """
    SELECT COUNT(DISTINCT assigned_engineer)
    FROM processed_tickets
    """
)

total_engineers = cursor.fetchone()[0]

# Current Status
system_status = "Running"


col1.metric(
    "Processed Tickets",
    total_tickets
)

col2.metric(
    "Active Engineers",
    total_engineers
)

col3.metric(
    "System Status",
    system_status
)


# Processed Tickets Table
st.subheader(
    "🎫 Processed Tickets"
)

query = """

SELECT *

FROM processed_tickets

"""

df = pd.read_sql_query(
    query,
    connection
)

st.dataframe(
    df,
    use_container_width=True
)


# Mock Ticket Viewer
st.subheader(
    "📥 Incoming Tickets"
)

with open(
        "data/mock_tickets.json",
        "r"
) as file:

    tickets = json.load(file)

tickets_df = pd.DataFrame(
    tickets
)

st.dataframe(
    tickets_df,
    use_container_width=True
)


# AI Routing Information
st.subheader(
    "🧠 AI Routing Engine"
)

st.success(
    "AI Routing Engine Active"
)

st.info(
    """
    Features Enabled:

    ✅ GPT Routing

    ✅ Fallback AI

    ✅ Confidence Scoring

    ✅ Escalation Logic

    ✅ Continuous Monitoring

    ✅ Notifications
    """
)


# Footer
st.markdown("---")

st.caption(
    "Enterprise Agentic AI Platform"
)

