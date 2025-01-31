from __future__ import annotations
from typing import TYPE_CHECKING
from streamlit.delta_generator import DeltaGenerator

if TYPE_CHECKING:
    from .follower import Follower


class State:

    auth_token: str = ""
    visit_profile: bool = False
    users_list: list[str] = []
    seconds_delay: int = 0
    minutes_delay: int = 0
    hours_delay: int = 0
    bot_is_running: bool = False
    state_line_text = ""
    follower: Follower | None = None
    state_line: DeltaGenerator = DeltaGenerator()

    @classmethod
    def update_state_line(cls, step: str) -> None:
        cls.state_line_text = step
        cls.state_line.text(cls.state_line_text)
        # st.rerun()
