import streamlit as st
import bcrypt

# Example user credentials
users = {
    "k": bcrypt.hashpw("123".encode('utf-8'), bcrypt.gensalt()),
    "acampbell": bcrypt.hashpw("King!".encode('utf-8'), bcrypt.gensalt()),
    "Ana": bcrypt.hashpw("123".encode('utf-8'), bcrypt.gensalt()),
    "James": bcrypt.hashpw("123".encode('utf-8'), bcrypt.gensalt())
}

# Dummy app content - import your real modules instead
from calculator import calculator
from calculation_history import calculation_history
from ch_calendar import show_event_calendar
from event_type import event_config
from staff_configuration import staff_config

def login():
    st.title("Login")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if username in users:
            if bcrypt.checkpw(password.encode('utf-8'), users[username]):
                st.success(f"Welcome {username}!")
                st.session_state.logged_in = True
                st.session_state.username = username
                st.rerun()
            else:
                st.error("Incorrect password!")
        else:
            st.error("Username not found!")

# Main logic
def main():
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False

    if not st.session_state.logged_in:
        login()
    else:
        st.sidebar.title(f"Welcome, {st.session_state.username}")
        page = st.sidebar.radio("Navigation", ["Calculator", "Calculation History", "Calendar", "Event Type Config", "Role Config", "Logout"])

        if page == "Calculator":
            calculator()
        elif page == "Calculation History":
            calculation_history()
        elif page == "Calendar":
            show_event_calendar(st.session_state.get("calculation_results", {}))
        elif page == "Event Type Config":
            event_config()
        elif page == "Role Config":
            staff_config()
        elif page == "Logout":
            st.session_state.logged_in = False
            st.rerun()

if __name__ == "__main__":
    main()

