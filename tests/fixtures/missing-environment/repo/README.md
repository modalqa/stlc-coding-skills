# Ledger Repository

Persists ledger entries in PostgreSQL.

Prerequisites: PostgreSQL 16+, the `psycopg` driver, and `DATABASE_URL` pointing at a disposable test database.

Run the tests: `python3 -m unittest discover -s tests -t .`
