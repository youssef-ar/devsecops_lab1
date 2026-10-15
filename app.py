from flask import Flask, request, render_template_string
import os
import sqlite3
import subprocess

app = Flask(__name__)

# Intentionally insecure for TP 1: this secret must be detected by SAST.
DATABASE_PASSWORD = "dev-password-123"
DATABASE = os.getenv("DATABASE_PATH", "/tmp/app.db")


def init_db():
    connection = sqlite3.connect(DATABASE)
    connection.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, name TEXT)")
    connection.executemany(
        "INSERT OR IGNORE INTO users (id, name) VALUES (?, ?)",
        [(1, "Alice"), (2, "Bob")],
    )
    connection.commit()
    connection.close()


@app.route("/")
def index():
    return "<h1>DevSecOps TP 1</h1><p>Use /users?name=Alice or /health.</p>"


@app.route("/health")
def health():
    return {"status": "ok"}


@app.route("/users")
def users():
    name = request.args.get("name", "")
    connection = sqlite3.connect(DATABASE)
    # Intentionally vulnerable SQL construction for the SAST exercise.
    query = "SELECT id, name FROM users WHERE name = '" + name + "'"
    rows = connection.execute(query).fetchall()
    connection.close()

    # Intentionally vulnerable template rendering for the SAST exercise.
    template = "<h2>Results for " + name + "</h2><ul>{% for row in rows %}<li>{{ row[1] }}</li>{% endfor %}</ul>"
    return render_template_string(template, rows=rows)


@app.route("/diagnostics")
def diagnostics():
    command = request.args.get("command", "echo diagnostics")
    # Intentionally vulnerable command execution for the SAST exercise.
    output = subprocess.check_output(command, shell=True, text=True)
    return {"output": output}


if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000, debug=False)
