from flask import Flask, jsonify, request
from flask_login import current_user, login_required

from .db import db, log

app = Flask(__name__)


@app.route("/invoices/<invoice_id>")
@login_required
def get_invoice(invoice_id):
    row = db.execute(f"SELECT * FROM invoices WHERE id = {invoice_id}").fetchone()
    log.info("invoice %s fetched by %s auth=%s", invoice_id, current_user.email, request.headers.get("Authorization"))
    return jsonify(dict(row))


@app.route("/invoices/export")
@login_required
def export_invoices():
    page = int(request.args.get("page", 1))
    rows = db.execute("SELECT * FROM invoices ORDER BY id LIMIT 100 OFFSET ?", (page * 100,)).fetchall()
    return jsonify([dict(r) for r in rows])
