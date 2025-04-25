import streamlit as st
import json
import os
import pandas as pd
from datetime import date
import altair as alt

# Load config files after login
def load_config_files():
    CONFIG_FILE = "staff_config.json"
    EVENT_CONFIG_FILE = "event_type_config.json"

    # Load existing staff config data
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            staff_config = json.load(f)
    else:
        staff_config = {}

    # Load existing event config data
    if os.path.exists(EVENT_CONFIG_FILE):
        with open(EVENT_CONFIG_FILE, "r") as f:
            event_config = json.load(f)
    else:
        event_config = {}

    return staff_config, event_config

def calculator():
    if "logged_in" not in st.session_state or not st.session_state.logged_in:
        st.error("You must be logged in to access this page!")
        return

    # Ensure 'calculation_results' exists in session state
    if "calculation_results" not in st.session_state or not isinstance(st.session_state.calculation_results, dict):
        st.session_state.calculation_results = {}

    # Get user ID from session
    user_id = st.session_state.get("username")
    if not user_id:
        st.error("User not logged in.")
        return

    # Load staff configuration
    staff_config = load_staff_config()

    # Fetch user event config from Firestore
    try:
        user_ref = db.collection('users').document(user_id)
        user_data = user_ref.get().to_dict()

        if not user_data:
            st.error("User data not found.")
            return

        # Print out user_data to debug
        st.write("User data:", user_data)

        # Get event_types from config
        event_types = user_data.get('config', {}).get('event_types', {})

        if not event_types:
            st.info("No event types configured. Please configure some first.")
            return

        # Build dropdown options from the keys of event_types
        event_type_names = list(event_types.keys())
        event_type = st.selectbox("Select Event Type", event_type_names)

    except Exception as e:
        st.error(f"Error fetching event types: {e}")
        return

    # Inputs
    col1, col2 = st.columns(2)
    with col1:
        num_guests = st.number_input("Enter the Number of Guests", min_value=1)
    with col2:
        event_date = st.date_input("Event Date", value=date.today())

    if st.button("Calculate Staff Costs"):
        if event_type and num_guests:
            selected_event = event_types.get(event_type)

            if not selected_event:
                st.warning("Selected event type not found.")
                return

            # You can now access the roles and numbers directly from selected_event
            for staff_role, num in selected_event.items():
                if staff_role not in staff_config:
                    st.warning(f"No staff configuration found for role '{staff_role}'.")
                    return

                ratio = staff_config[staff_role].get('ratio', 1)
                hourly_rate = staff_config[staff_role].get('per_hour', 0)

                staff_count = (num_guests + ratio - 1) // ratio
                total_cost = staff_count * hourly_rate * 10  # Assuming hours are fixed at 10

                staff_needed = [{
                    "Role": staff_role,
                    "Staff Required": staff_count,
                    "Hourly Rate (£)": hourly_rate,
                    "Hours": 10,
                    "Total Cost (£)": total_cost
                }]

                df_staff = pd.DataFrame(staff_needed)
                st.dataframe(df_staff)

                total_staff = df_staff["Staff Required"].sum()
                total_event_cost = df_staff["Total Cost (£)"].sum()

                key = f"{event_type}_{event_date}"
                st.session_state.calculation_results[key] = {
                    "event_type": event_type,
                    "event_date": str(event_date),
                    "guests": num_guests,
                    "staff_needed": staff_needed,
                    "total_cost": total_event_cost,
                    "total_staff": total_staff
                }

                # Summary Table
                df_costs = pd.DataFrame([{
                    "Event": event_type,
                    "Total Cost (£)": total_event_cost,
                    "Total Staff": total_staff,
                    "Guests": num_guests, 
                    "Date": str(event_date)
                }])

                st.dataframe(
                    df_costs,
                    use_container_width=True,
                    hide_index=True,
                    column_config={
                        "Total Cost (£)": st.column_config.NumberColumn(format="£%.2f")
                    }
                )

                # Altair Chart
                cost_chart = alt.Chart(df_staff).mark_bar().encode(
                    x=alt.X("Role:N", title="Role", axis=alt.Axis(labelAngle=-45)),
                    y=alt.Y("Total Cost (£):Q", title="Cost in £"),
                    color=alt.Color("Role:N"),
                    tooltip=["Role", "Staff Required", "Hourly Rate (£)", "Hours", "Total Cost (£)"]
                ).properties(
                    title="Cost Breakdown by Role",
                    width=600,
                    height=400
                )

                st.altair_chart(cost_chart, use_container_width=True)
                st.divider()

        else:
            st.warning("Please select an event type and enter the number of guests.")
