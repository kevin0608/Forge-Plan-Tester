import altair as alt
import streamlit as st
import pandas as pd

def calculation_history():
    st.title("Previous Calculations")

    # Ensure session state is initialized
    if "calculation_results" not in st.session_state:
        st.session_state.calculation_results = []

    table_data = []

    if st.session_state.calculation_results:
        for event, result in st.session_state.calculation_results.items():
            # Check if result is a dictionary and handle it accordingly
            if isinstance(result, dict):
                event_type = result.get("event_type", "N/A")
                st.markdown(f"### {event_type}")
                df_prev = pd.DataFrame(result["staff_needed"])
                st.dataframe(df_prev)

                # Construct the table for displaying the history
                row = {
                    "Event": result.get("event_type", "N/A"),
                    "Total Cost (£)": f"£{result['total_cost']:.2f}",
                    "Total Staff": result.get("total_staff"),
                    "Guests": result.get("guests", "N/A"),  # Use .get() for optional fields
                    "Date": result.get("event_date", "N/A")
                }
                table_data.append(row)

            # 🔍 Chart: Total Cost by Role for This Event
            cost_chart = alt.Chart(df_prev).mark_bar().encode(
                x=alt.X("Role:N", title="Role", axis=alt.Axis(labelAngle=-45)),
                y=alt.Y("Total Cost (£):Q", title="Cost in £"),
                color=alt.Color("Role:N"),
                tooltip=["Role", "Staff Required", "Hourly Rate (£)", "Total Cost (£)"]
            ).properties(
                title=f"Cost Breakdown by Role - {event_type}",
                width=600,
                height=300
            )
            st.altair_chart(cost_chart, use_container_width=True)

        # Show summary table only once after loop
        if table_data:
            df_costs = pd.DataFrame(table_data)
            st.dataframe(
                df_costs,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Total Cost (£)": st.column_config.NumberColumn(format="£%.2f")
                }
            )

    else:
        st.info("No calculations history available.")

        # Divider after showing no results info
        st.divider()
