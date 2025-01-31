import time
import streamlit as st
from app.follower import Follower
from app.state import State


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
