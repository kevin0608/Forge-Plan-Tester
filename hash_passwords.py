import streamlit as st
import bcrypt

# Example user credentials (username and password) - Normally, you'd store these securely, not in the code.
# For now, let's hardcode a test user
users = {
    "user1": bcrypt.hashpw("yourpassword".encode('utf-8'), bcrypt.gensalt()),
    "user2": bcrypt.hashpw("anotherpassword".encode('utf-8'), bcrypt.gensalt())
}

# Streamlit login page
def login():
    # Ask for username and password
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if username in users:
            # Check if the entered password matches the stored hashed password
            if bcrypt.checkpw(password.encode('utf-8'), users[username]):
                st.success(f"Welcome {username}!")
                return True
            else:
                st.error("Incorrect password!")
        else:
            st.error("Username not found!")
    return False

# Main Streamlit app
def main():
    st.title("Streamlit Login Example")

    if login():
        st.write("You are now logged in!")

if __name__ == "__main__":
    main()
