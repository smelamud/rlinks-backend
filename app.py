import os

from flask import Flask, Response

import db

app = Flask(__name__)

@app.post("/test")
def test_endpoint():
    # Execute the same logic previously in main() and return its textual output
    outputs: list[str] = []
    config = app.config["DB_CONFIG"]
    with db.Graph(config) as graph:
        with graph.cursor() as cursor:
            cursor.execute("CREATE (:App {name: 'MyApp', version: '1.0'})")
            for a in cursor.query("MATCH (a:App) RETURN a"):
                outputs.append(str(a))
            cursor.query("MATCH (a:App) DELETE a")
    result = "\n".join(outputs)
    return Response(result, content_type="text/plain; charset=utf-8")


if __name__ == "__main__":
    app.config["DB_CONFIG"] = db.load_config()
    app.run(
        host=os.getenv("FLASK_HOST", "0.0.0.0"),
        port=int(os.getenv("FLASK_PORT", "8000")),
        debug=False,
    )
