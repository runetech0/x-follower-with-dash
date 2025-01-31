from playwright.sync_api import sync_playwright, TimeoutError
from .state import State


class Follower:

    def __init__(self, auth_token: str) -> None:
        self._headless = True
        self._auth_token = auth_token

    def stop(self) -> None:
        self._browser.close()

    def start(self) -> None:
        self._browser = (
            sync_playwright().start().firefox.launch(headless=self._headless)
        )
        State.update_state_line("Creating browser context ...")

        self._ctx = self._browser.new_context()
        self._ctx.add_cookies(
            [
                {
                    "name": "auth_token",
                    "value": self._auth_token,
                    "domain": "x.com",
                    "path": "/",
                }
            ]
        )
        State.update_state_line("Loading cookies ...")
        self._page = self._ctx.new_page()
        self._page.set_default_navigation_timeout(100000)
        State.update_state_line("Waiting for x.com ...")
        self._page.goto("https://x.com/home")

    def follow_user(self, username: str) -> None:
        State.update_state_line(f"Opening {username} profile ...")
        username = username.replace("@", "").strip()
        url = f"https://x.com/{username}"
        self._page.goto(url)

        # time.sleep(5000)
        State.update_state_line(f"Following {username} ...")
        follow_button = self._page.get_by_label(f"Follow @{username}", exact=True)
        try:
            follow_button.click(force=True)

        except TimeoutError:
            pass

        State.update_state_line(f"Followed @{username}")
        return print("Followed user!")

    def save_screenshot(self) -> None:
        data = self._page.screenshot()
        with open("ss.png", mode="wb") as f:
            f.write(data)
