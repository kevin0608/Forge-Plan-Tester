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

    # Ensure that 'calculation_results' is always a dictionary
    if "calculation_results" not in st.session_state or not isinstance(st.session_state.calculation_results, dict):
        st.session_state.calculation_results = {}

    staff_config, event_config = load_config_files()

    st.title("Staffing Calculator")

    event_type = st.selectbox("Select Event Type", list(event_config.keys()))

    col1, col2 = st.columns(2)
    with col1:
        num_guests = st.number_input("Enter the Number of Guests", min_value=1)
    with col2:
        event_date = st.date_input("Event Date", value=date.today())

    if st.button("Calculate Staff Costs"):
        if event_type and num_guests:
            staff_needed = []

            # Iterate through roles and use override hours if present
            for role, override_hours in event_config[event_type].items():
                if role in staff_config:
                    ratio = staff_config[role]['ratio']
                    hourly_rate = staff_config[role]['per_hour']
                    default_hours = staff_config[role].get('hours', 8)
                    hours = override_hours if override_hours else default_hours

                    staff_count = (num_guests + ratio - 1) // ratio
                    total_cost = staff_count * hourly_rate * hours

                    staff_needed.append({
                        "Role": role,
                        "Staff Required": staff_count,
                        "Hourly Rate (£)": hourly_rate,
                        "Hours": hours,
                        "Total Cost (£)": total_cost
                    })

            if staff_needed:
                df_staff = pd.DataFrame(staff_needed)
                st.dataframe(df_staff)
                total_staff = df_staff["Staff Required"].sum()

                key = f"{event_type}_{event_date}"
                st.session_state.calculation_results[key] = {
                    "event_type": event_type,
                    "event_date": str(event_date),
                    "guests": num_guests,
                    "staff_needed": staff_needed,
                    "total_cost": df_staff["Total Cost (£)"].sum(),
                    "total_staff": total_staff
                }

                df_costs = pd.DataFrame([{
                    "Event": event_type,
                    "Total Cost (£)": df_staff["Total Cost (£)"].sum(),
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
                st.info("No valid roles for the selected event type.")
        else:
            st.warning("Please select an event type and enter the number of guests.")
