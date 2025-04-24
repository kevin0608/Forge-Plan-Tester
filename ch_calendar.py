from streamlit_calendar import calendar
from datetime import datetime
import streamlit as st
import uuid
import pandas as pd
import hashlib
import json
import io

def hash_data(data):
    """Create a hash of the input data for caching comparison."""
    return hashlib.md5(json.dumps(data, sort_keys=True).encode()).hexdigest()

@st.cache_data(show_spinner=False)

def generate_events(calculations):
    """Generate calendar events from calculation data."""
    events = []
    for key, data in calculations.items():
        event_date = data.get("event_date")
        if event_date:
            try:
                date_obj = datetime.strptime(event_date, "%Y-%m-%d")
                events.append({
                    "Event": f"{data['event_type']}",
                    "Date": date_obj.strftime("%Y-%m-%d")
                })
            except Exception as e:
                st.warning(f"Invalid date '{event_date}': {e}")
    return events

def convert_to_csv(events):
    """Convert events list to CSV format."""
    df = pd.DataFrame(events)
    csv = df.to_csv(index=False)
    return csv

def show_event_calendar(calculations):
    st.title("Calendar")

    if not calculations:
        st.info("No events recorded yet.")
        return

    events = generate_events(calculations)

    # Show the calendar
    calendar(
        events=events,
        options={
            "initialView": "dayGridMonth",
            "editable": False,
            "selectable": True
        }
    )

    # Add a download button for the events
    if events:
        csv = convert_to_csv(events)
        st.download_button(
            label="Download Events as CSV",
            data=csv,
            file_name="events_calendar.csv",
            mime="text/csv"
        )
