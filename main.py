import time
import streamlit as st
from app.follower import Follower
from app.state import State
import json
from streamlit_cookies_manager import CookieManager  # type: ignore

# ================= LOGIN PAGE WITH COOKIES ================= #

# Define the correct password
CORRECT_PASSWORD = "MGWW-Bart010"

# Initialize Cookies Manager
cookies = CookieManager()

# Ensure session state variables are initialized
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if "users_list" not in st.session_state:
    st.session_state["users_list"] = []  # ✅ Initialize as a list

# Ensure bot state variables are initialized
if not hasattr(State, "bot_is_running"):
    State.bot_is_running = False

if not hasattr(State, "users_list"):
    State.users_list = []

# Wait for cookies to be ready before using them
if not cookies.ready():
    st.warning("Waiting for cookies to be ready...")
    time.sleep(1)
    st.rerun()

# Load authentication status from cookies
auth_cookie = cookies.get("auth_status")
if auth_cookie:
    try:
        st.session_state.authenticated = json.loads(auth_cookie)
    except json.JSONDecodeError:
        st.session_state.authenticated = False
else:
    st.session_state.authenticated = False

# Show login page if not authenticated
if not st.session_state.authenticated:
    st.title("🔒 Login")
    password = st.text_input("Enter Password:", type="password")

    if st.button("Login"):
        if password == CORRECT_PASSWORD:
            st.session_state.authenticated = True
            cookies["auth_status"] = json.dumps(True)
            cookies.save()
            st.success("✅ Login successful! Redirecting...")
            time.sleep(1)
            st.rerun()
        else:
            st.error("❌ Incorrect password. Try again.")

    st.stop()


# ================= ADD LOGOUT OPTION ================= #
def logout() -> None:
    cookies["auth_status"] = json.dumps(False)
    cookies.save()
    st.session_state.authenticated = False
    st.session_state.pop("authenticated", None)  # ✅ Only remove authentication key
    st.success("✅ Logged out successfully. Redirecting to login...")
    time.sleep(1)
    st.rerun()


st.sidebar.button("🚪 Logout", on_click=logout)


# ================= MAIN APPLICATION ================= #


header_text = "X Follower Bot"
st.markdown(
    f"<h1 style='text-align: center;'>{header_text}</h1>", unsafe_allow_html=True
)

State.auth_token = st.text_input(
    "User auth_token", State.auth_token, disabled=State.bot_is_running
)


def add_user_to_list() -> None:
    new_users_list: str = st.session_state["users_list"]
    State.users_list = new_users_list.strip().split("\n")


st.text_area(
    "Users List",
    "\n".join(State.users_list),
    on_change=add_user_to_list,
    key="users_list",
    disabled=State.bot_is_running,
)


st.markdown(
    """
    <h4>Delay between each follow<h4>
""",
    unsafe_allow_html=True,
)


hour_col, min_col, sec_col = st.columns(3)

State.hours_delay = hour_col.number_input(
    "Hours:",
    min_value=0,
    max_value=24,
    value=State.hours_delay,
    step=1,
    key="hours_delay",
    disabled=State.bot_is_running,
)
State.minutes_delay = min_col.number_input(
    "Minutes:",
    min_value=0,
    max_value=59,
    value=State.minutes_delay,
    step=1,
    key="minutes_delay",
    disabled=State.bot_is_running,
)
State.seconds_delay = sec_col.number_input(
    "Seconds:",
    min_value=0,
    max_value=59,
    value=State.seconds_delay,
    step=1,
    key="seconds_delay",
    disabled=State.bot_is_running,
)

# Convert total delay into seconds
total_delay = (
    (State.hours_delay * 3600) + (State.minutes_delay * 60) + State.seconds_delay
)
st.text(f"Total delay: {total_delay} seconds")


def run_bot() -> None:
    if not State.auth_token:
        st.toast("Missing auth_token")
        return

    if not State.users_list:
        st.toast("Add users to follow!")
        return

    State.bot_is_running = True
    State.update_state_line("Running the bot ...")


st.button("Run bot", on_click=run_bot, key="run_bot")


def stop_bot() -> None:
    State.bot_is_running = False
    State.update_state_line("No running")
    if State.follower:
        State.follower.stop()
        State.follower = None
    print("Bot stopped!")


if State.bot_is_running:
    State.state_line = st.empty()

    State.update_state_line(State.state_line_text)
    st.button("Stop Bot", on_click=stop_bot)

    if not State.follower and State.users_list:
        State.follower = Follower(State.auth_token)
        State.follower.start()

        for user in State.users_list:
            State.follower.follow_user(user)

            State.update_state_line(
                f"Waiting for {total_delay} seconds before following next user ..."
            )
            time.sleep(total_delay)

        State.update_state_line("No more users to follow!")
        stop_bot()
        st.rerun()
