"""Ledger persistence on PostgreSQL."""
import os
from decimal import Decimal

import psycopg  # third-party driver; must be installed in the test environment


def connect():
    return psycopg.connect(os.environ["DATABASE_URL"])


class Ledger:
    def __init__(self, conn) -> None:
        self.conn = conn

    def record(self, account: str, amount: Decimal) -> None:
        if amount == 0:
            raise ValueError("amount must be non-zero")
        with self.conn.transaction():
            self.conn.execute("INSERT INTO entries(account, amount) VALUES (%s, %s)", (account, amount))
            self.conn.execute(
                "INSERT INTO balances(account, balance) VALUES (%s, %s) "
                "ON CONFLICT (account) DO UPDATE SET balance = balances.balance + EXCLUDED.balance",
                (account, amount))

    def balance(self, account: str) -> Decimal:
        row = self.conn.execute("SELECT balance FROM balances WHERE account = %s", (account,)).fetchone()
        return row[0] if row else Decimal("0")
