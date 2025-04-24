import streamlit as st
import json
import os
import pandas as pd

EVENT_CONFIG_FILE = "event_type_config.json"
STAFF_CONFIG_FILE = "staff_config.json"

def event_config():
    # Load staff role data from JSON
    if os.path.exists(STAFF_CONFIG_FILE):
        with open(STAFF_CONFIG_FILE, "r") as f:
            staff_config = json.load(f)
    else:
        staff_config = {}

    # Load event types if exists
    if os.path.exists(EVENT_CONFIG_FILE):
        with open(EVENT_CONFIG_FILE, "r") as f:
            event_config = json.load(f)
    else:
        event_config = {}

    st.title("Event Type Configuration")

    st.subheader("Add New Event Type")

    event_name = st.text_input("Event Type Name")

    # Initialize to prevent UnboundLocalError
    selected_roles = []

    if staff_config:
        selected_roles = st.multiselect(
            "Select Roles for this Event",
            list(staff_config.keys()),
            format_func=lambda r: f"{r} (1 per {staff_config[r]['ratio']}, £{staff_config[r]['per_hour']}/hr, default {staff_config[r]['hours']} hrs)"
        )
    else:
        st.warning("No roles available. Please configure roles first.")

    # Dictionary to store selected roles with override hours
    role_with_hours = {}

    # Only define and run override if roles are selected
    if selected_roles:
        def override():
            st.subheader("Override Default Hours (Optional)")
            for role in selected_roles:
                default_hours = staff_config[role].get("hours", 8)
                override_val = st.number_input(
                    f"{role} - Default: {default_hours} hrs → Override:",
                    min_value=0.0,
                    step=0.5,
                    key=f"override_{role}"
                )
                # Store 0 to indicate using default, or custom override if > 0
                role_with_hours[role] = override_val

        override()


    if st.button("Save Event Type"):
        if event_name and role_with_hours:
            event_config[event_name] = role_with_hours
            with open(EVENT_CONFIG_FILE, "w") as f:
                json.dump(event_config, f, indent=4)
            st.success(f"Event type '{event_name}' saved!")
        else:
            st.error("Event name and at least one role must be provided.")

    st.divider()

    if st.button("Clean Up Invalid Event Types"):
        removed_events = []
        valid_roles = set(staff_config.keys())

        for event_name in list(event_config.keys()):
            event_roles = event_config[event_name]
            if any(role not in valid_roles for role in event_roles):
                removed_events.append(event_name)
                del event_config[event_name]

        if removed_events:
            with open(EVENT_CONFIG_FILE, "w") as f:
                json.dump(event_config, f, indent=4)
            st.success(f"Removed {len(removed_events)} event type(s): {', '.join(removed_events)}")
        else:
            st.info("No invalid event types found.")

    st.subheader("Existing Event Types")

    if event_config:
        event_data = []
        for event, roles in event_config.items():
            for role, override_hours in roles.items():
                default_hours = staff_config.get(role, {}).get("hours", 8)
                shown_hours = override_hours if override_hours > 0 else default_hours
                event_data.append({
                    "Event Type": event,
                    "Role": role,
                    "Guests per Staff": staff_config.get(role, {}).get("ratio", "-"),
                    "Hourly Rate (£)": staff_config.get(role, {}).get("per_hour", "-"),
                    "Hours Used": shown_hours,
                    "Hours Source": "Override" if override_hours > 0 else "Default"
                })

        df_event = pd.DataFrame(event_data)
        st.dataframe(df_event, use_container_width=True)
    else:
        st.info("No event types configured yet.")
