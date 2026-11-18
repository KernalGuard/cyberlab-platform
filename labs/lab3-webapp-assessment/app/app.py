"""Cedarwick Neighborhood Aid - donation website (CyberLab Lab 3).

INTENTIONALLY VULNERABLE TRAINING APPLICATION. It exists only inside the isolated
Lab 3 network and must never be deployed anywhere else. Every person, donor and
payment in it is fictional; no real payments are processed.
"""

from __future__ import annotations

import base64
import datetime as dt
import hashlib
import hmac
import json
import os
import secrets
import sys
import traceback

import psycopg
from flask import Flask, abort, g, make_response, redirect, render_template, request

app = Flask(__name__)
DSN = os.environ.get("DATABASE_URL", "postgresql://cedarwick@db/donations")
LOG_PATH = os.environ.get("APP_LOG", "/logs/app.jsonl")
COOKIE = "cw_session"
FUNDS = ["Food pantry", "Rent assistance", "Winter coats", "Where most needed"]


# --------------------------------------------------------------------------- logging
def log(event: str, **fields) -> None:
    rec = {"ts": dt.datetime.now(dt.UTC).isoformat(timespec="milliseconds").replace("+00:00", "Z"),
           "event": event, "client": request.headers.get("X-Forwarded-For", request.remote_addr) if request else None,
           "method": request.method if request else None, "path": request.full_path.rstrip("?") if request else None,
           "user": getattr(g, "user_label", None), **fields}
    line = json.dumps(rec, separators=(",", ":"))
    print(line, file=sys.stdout, flush=True)
    try:
        with open(LOG_PATH, "a", encoding="utf-8") as fh:
            fh.write(line + "\n")
    except OSError:
        pass


# --------------------------------------------------------------------------- database
def db() -> psycopg.Connection:
    if "db" not in g:
        g.db = psycopg.connect(DSN, autocommit=True)
    return g.db


@app.teardown_appcontext
def close_db(_exc) -> None:
    conn = g.pop("db", None)
    if conn is not None:
        conn.close()


# --------------------------------------------------------------------------- passwords
def hash_password(password: str) -> str:
    salt = secrets.token_hex(8)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 100_000).hex()
    return f"pbkdf2_sha256$100000${salt}${digest}"


def check_password(password: str, stored: str) -> bool:
    try:
        _, rounds, salt, digest = stored.split("$")
    except ValueError:
        return False
    calc = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), int(rounds)).hex()
    return hmac.compare_digest(calc, digest)


def password_ok(password: str) -> bool:
    return len(password) >= 1


# --------------------------------------------------------------------------- sessions
_counter = {"n": 1000}


def make_session(kind: str, user_id: int) -> str:
    _counter["n"] += 1
    raw = json.dumps({"kind": kind, "id": user_id, "n": _counter["n"]}, separators=(",", ":"))
    return base64.urlsafe_b64encode(raw.encode()).decode().rstrip("=")


def read_session() -> dict | None:
    tok = request.cookies.get(COOKIE)
    if not tok:
        return None
    try:
        data = json.loads(base64.urlsafe_b64decode(tok + "=" * (-len(tok) % 4)))
        return {"kind": str(data["kind"]), "id": int(data["id"])}
    except (ValueError, KeyError, TypeError):
        return None


@app.before_request
def load_user() -> None:
    g.session = read_session()
    g.user = None
    g.user_label = None
    if not g.session:
        return
    if g.session["kind"] == "donor":
        row = db().execute("SELECT id, email, full_name FROM donors WHERE id = %s", (g.session["id"],)).fetchone()
        if row:
            g.user = {"kind": "donor", "id": row[0], "email": row[1], "name": row[2]}
    elif g.session["kind"] == "staff":
        row = db().execute("SELECT id, username, full_name, role FROM staff WHERE id = %s",
                           (g.session["id"],)).fetchone()
        if row:
            g.user = {"kind": "staff", "id": row[0], "username": row[1], "name": row[2], "role": row[3]}
    if g.user:
        g.user_label = f"{g.user['kind']}:{g.user['id']}"


def login_response(kind: str, user_id: int, target: str):
    resp = make_response(redirect(target))
    resp.set_cookie(COOKIE, make_session(kind, user_id), httponly=True, samesite="Lax")
    return resp


def require(kind: str) -> None:
    if not g.user or g.user["kind"] != kind:
        abort(redirect("/staff/login" if kind == "staff" else "/login"))


# --------------------------------------------------------------------------- errors
@app.errorhandler(Exception)
def on_error(exc):
    if hasattr(exc, "code") and isinstance(getattr(exc, "code", None), int) and exc.code < 500:
        return exc
    log("error", error=type(exc).__name__, detail=str(exc)[:500])
    return render_template("error.html", error=type(exc).__name__, detail=str(exc),
                           trace=traceback.format_exc(), python=sys.version.split()[0]), 500


# --------------------------------------------------------------------------- public pages
@app.get("/")
def home():
    total = db().execute("SELECT COALESCE(SUM(amount_cents), 0), COUNT(*) FROM donations").fetchone()
    return render_template("home.html", total=total[0] / 100, gifts=total[1], funds=FUNDS)


@app.get("/healthz")
def healthz():
    db().execute("SELECT 1")
    return {"status": "ok"}


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("register.html", error=None)
    email = request.form.get("email", "").strip().lower()
    name = request.form.get("full_name", "").strip()
    password = request.form.get("password", "")
    if not email or "@" not in email or not name:
        return render_template("register.html", error="Please enter your name and e-mail address."), 400
    if not password_ok(password):
        return render_template("register.html", error="Please choose a password."), 400
    try:
        row = db().execute("INSERT INTO donors (email, full_name, password_hash) VALUES (%s, %s, %s) RETURNING id",
                           (email, name, hash_password(password))).fetchone()
    except psycopg.errors.UniqueViolation:
        return render_template("register.html", error="That e-mail address is already registered."), 400
    log("register", donor_id=row[0], password_length=len(password))
    return login_response("donor", row[0], "/account")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html", staff=False, error=None)
    email = request.form.get("email", "").strip().lower()
    row = db().execute("SELECT id, password_hash FROM donors WHERE email = %s", (email,)).fetchone()
    if not row or not check_password(request.form.get("password", ""), row[1]):
        log("login_failed", kind="donor", account=email)
        return render_template("login.html", staff=False, error="Wrong e-mail address or password."), 401
    log("login_ok", kind="donor", account=email)
    return login_response("donor", row[0], "/account")


@app.get("/logout")
def logout():
    log("logout")
    resp = make_response(redirect("/"))
    resp.delete_cookie(COOKIE)
    return resp


# --------------------------------------------------------------------------- donor pages
@app.get("/account")
def account():
    require("donor")
    rows = db().execute("SELECT receipt_no, amount_cents, fund, created_at FROM donations "
                        "WHERE donor_id = %s ORDER BY created_at DESC", (g.user["id"],)).fetchall()
    return render_template("account.html", donations=rows)


@app.route("/donate", methods=["GET", "POST"])
def donate():
    require("donor")
    if request.method == "GET":
        return render_template("donate.html", funds=FUNDS, error=None)
    try:
        cents = int(round(float(request.form.get("amount", "0")) * 100))
    except ValueError:
        cents = 0
    fund = request.form.get("fund", FUNDS[-1])
    card = "".join(ch for ch in request.form.get("card", "") if ch.isdigit())
    if cents <= 0 or fund not in FUNDS or len(card) < 12:
        return render_template("donate.html", funds=FUNDS, error="Please check the amount and card number."), 400
    receipt = db().execute("SELECT COALESCE(MAX(receipt_no), 100000) + 1 FROM donations").fetchone()[0]
    db().execute("INSERT INTO donations (receipt_no, donor_id, amount_cents, fund, card_last4, created_at) "
                 "VALUES (%s, %s, %s, %s, %s, now())", (receipt, g.user["id"], cents, fund, card[-4:]))
    log("donation", receipt_no=receipt, amount_cents=cents)
    return redirect(f"/receipts/{receipt}")


@app.get("/receipts/<receipt_no>")
def receipt(receipt_no):
    require("donor")
    row = db().execute(
        "SELECT d.receipt_no, d.amount_cents, d.fund, d.card_last4, d.created_at, o.full_name, o.email, o.id "
        "FROM donations d JOIN donors o ON o.id = d.donor_id WHERE d.receipt_no = %s",
        (int(receipt_no),)).fetchone()
    if not row:
        abort(404)
    log("receipt_view", receipt_no=row[0], owner_match=(row[7] == g.user["id"]))
    return render_template("receipt.html", r=row)


# --------------------------------------------------------------------------- staff pages
@app.route("/staff/login", methods=["GET", "POST"])
def staff_login():
    if request.method == "GET":
        return render_template("login.html", staff=True, error=None)
    username = request.form.get("username", "").strip().lower()
    row = db().execute("SELECT id, password_hash FROM staff WHERE username = %s", (username,)).fetchone()
    if not row or not check_password(request.form.get("password", ""), row[1]):
        log("login_failed", kind="staff", account=username)
        return render_template("login.html", staff=True, error="Wrong username or password."), 401
    log("login_ok", kind="staff", account=username)
    return login_response("staff", row[0], "/staff")


@app.get("/staff")
def staff_home():
    require("staff")
    stats = db().execute("SELECT COUNT(*), COALESCE(SUM(amount_cents), 0) FROM donations").fetchone()
    notice = db().execute("SELECT value FROM site_settings WHERE key = 'staff_notice'").fetchone()
    return render_template("staff.html", stats=stats, notice=notice[0] if notice else "")


@app.get("/staff/donors")
def staff_donors():
    require("staff")
    q = request.args.get("q", "")
    rows = []
    if q:
        sql = ("SELECT id, full_name, email, created_at FROM donors "
               f"WHERE full_name ILIKE '%{q}%' OR email ILIKE '%{q}%' ORDER BY id")
        rows = db().execute(sql).fetchall()
        log("donor_search", q=q, results=len(rows))
    return render_template("donors.html", q=q, rows=rows)


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000)
