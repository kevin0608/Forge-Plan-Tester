import streamlit as st
import json
import os
import pandas as pd

CONFIG_FILE = "staff_config.json"

def staff_config():
    # Load existing data if available
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            staff_config = json.load(f)
    else:
        staff_config = {}

    st.title("Role Configuration")

    with st.form("staff_form"):
        role = st.text_input("Role (e.g. waiter, bartender, chef, security, nurse)")
        ratio = st.number_input("Ratio (e.g. 25 guests/room/patient/students per staff)", min_value=1)
        per_hour = st.number_input("Hourly Rate", min_value=0.0, step=0.5)
        hours = st.number_input("Hours", min_value=0.0, step=0.5)
        submitted = st.form_submit_button("Add / Update Role")

        if submitted:
            if role:
                staff_config[role] = {
                    "ratio": int(ratio),
                    "per_hour": float(per_hour),
                    "hours": float(hours)
                }
                with open(CONFIG_FILE, "w") as f:
                    json.dump(staff_config, f, indent=4)
                st.success(f"{role} saved!")
            else:
                st.error("Role name cannot be empty.")

    st.subheader("Current Configuration")

    if staff_config:
        sorted_roles = dict(sorted(staff_config.items()))
        df = pd.DataFrame.from_dict(sorted_roles, orient='index')
        df.index.name = "Role"
        st.dataframe(df, use_container_width=True)

        st.markdown("### Delete Individual Roles")
        roles_to_delete = st.multiselect("Select Role(s) to Delete", list(sorted_roles.keys()))

        if roles_to_delete and st.button("Delete Selected"):
            for role in roles_to_delete:
                staff_config.pop(role, None)
            with open(CONFIG_FILE, "w") as f:
                json.dump(staff_config, f, indent=4)
            st.success(f"Deleted: {', '.join(roles_to_delete)}")
            st.rerun()

    else:
        st.info("No roles configured.")
