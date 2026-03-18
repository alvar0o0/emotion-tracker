import streamlit as st
import pandas as pd
import altair as alt
from sqlalchemy import create_engine
import datetime
import logging

# Configure logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# Database setup
DATABASE_URL = "sqlite:///./emotions.db"
engine = create_engine(DATABASE_URL)

def get_data():
    """Fetches data from the database and returns it as a DataFrame."""
    logger.info("Fetching data from database for dashboard")
    try:
        query = "SELECT emotion, level, timestamp FROM emotion_logs"
        df = pd.read_sql(query, engine)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        logger.info("Successfully fetched %d rows", len(df))
        return df
    except Exception as e:
        logger.error("Error fetching data from database: %s", e)
        return pd.DataFrame()

def main():
    st.title("Emotion Tracker Dashboard")

    df = get_data()

    if df.empty:
        st.warning("No emotion data logged yet.")
        return

    # Bar chart of emotion counts
    st.header("Emotion Counts")
    emotion_counts = df['emotion'].value_counts().reset_index()
    emotion_counts.columns = ['emotion', 'count']
    bar_chart = alt.Chart(emotion_counts).mark_bar().encode(
        x='emotion',
        y='count'
    ).properties(
        width=alt.Step(80)  # controls width of bars
    )
    st.altair_chart(bar_chart, use_container_width=True)

    # Timeline of emotions for today
    st.header("Today's Emotions")
    today = datetime.date.today()
    today_df = df[df['timestamp'].dt.date == today]

    if today_df.empty:
        st.info("No emotions logged today.")
    else:
        timeline_chart = alt.Chart(today_df).mark_line().encode(
            x='timestamp',
            y='level',
            color='emotion'
        ).properties(
            title="Emotion Levels Over Time Today"
        )
        st.altair_chart(timeline_chart, use_container_width=True)

if __name__ == "__main__":
    main()
