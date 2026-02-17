from flask import Blueprint, request, jsonify
from app.middleware import require_api_key
from app.services.report_service import sales_summary, low_stock

report_bp = Blueprint("report", __name__)


@report_bp.route("/api/v1/reports/sales-summary")
@require_api_key()
def sales():
    return sales_summary()


@report_bp.route("/api/v1/reports/low-stock")
@require_api_key()
def low():

    threshold = request.args.get("threshold", type=int)

    if threshold is None:
        return jsonify({"error":"threshold required"}),400

    return low_stock(threshold)
