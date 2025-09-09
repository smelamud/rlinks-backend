from __future__ import annotations

from db import query


def main() -> None:
    # Simple interaction: fetch the current database name to verify connectivity
    rows = query("SELECT current_database()")
    dbname = rows[0][0] if rows else "<unknown>"
    print(f"Connected to PostgreSQL database: {dbname}")


if __name__ == "__main__":
    main()
