from __future__ import annotations

import db


def main() -> None:
    config = db.load_config()
    with db.Graph(config) as graph:
        with graph.cursor() as cursor:
            cursor.execute("CREATE (:App {name: 'MyApp', version: '1.0'})")
            for a in cursor.query("MATCH (a:App) RETURN a"):
                print(a)
            cursor.query("MATCH (a:App) DELETE a")


if __name__ == "__main__":
    main()
