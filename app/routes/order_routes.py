from flask import Blueprint, request, jsonify
from app.middleware import require_api_key
from app.services.order_service import create_order, load_orders, update_status, cancel_order

order_bp = Blueprint("order", __name__)


@order_bp.route("/api/v1/orders", methods=["POST"])
@require_api_key()
def create():

    result = create_order(request.json)

    # handle service returning (data,status)
    if isinstance(result, tuple):
        return jsonify(result[0]), result[1]

    return jsonify(result), 200


@order_bp.route("/api/v1/orders")
@require_api_key()
def list_orders():

    orders = load_orders()

    status = request.args.get("status")
    email = request.args.get("customer_email")

    if status:
        orders = [o for o in orders if o["status"] == status]

    if email:
        orders = [o for o in orders if o["customer_email"] == email]

    return jsonify(orders)


@order_bp.route("/api/v1/orders/<oid>/status", methods=["PATCH"])
@require_api_key()
def status(oid):

    result = update_status(oid, request.json["status"])

    if isinstance(result, tuple):
        return jsonify(result[0]), result[1]

    return jsonify(result)


@order_bp.route("/api/v1/orders/<oid>/cancel", methods=["POST"])
@require_api_key()
def cancel(oid):

    result = cancel_order(oid)

    if isinstance(result, tuple):
        return jsonify(result[0]), result[1]

    return jsonify(result)
