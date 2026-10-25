"""Account rules (implementation follows draft v2)."""

MIN_PASSWORD_LENGTH = 8
MAX_FAILED_ATTEMPTS = 5


class AccountError(Exception):
    pass


class Accounts:
    def __init__(self) -> None:
        self.users: dict[str, dict] = {}

    def register(self, username: str, password: str) -> None:
        if username in self.users:
            raise AccountError("username taken")
        if len(password) < MIN_PASSWORD_LENGTH:
            raise AccountError("password too short")
        self.users[username] = {"password": password, "failed": 0, "locked": False, "active": True}

    def login(self, username: str, password: str) -> bool:
        user = self.users.get(username)
        if user is None or user["locked"] or not user["active"]:
            return False
        if user["password"] != password:
            user["failed"] += 1
            user["locked"] = user["failed"] >= MAX_FAILED_ATTEMPTS
            return False
        user["failed"] = 0
        return True

    def delete(self, username: str, actor_role: str) -> None:
        if actor_role != "admin":
            raise AccountError("forbidden")
        self.users.pop(username, None)
