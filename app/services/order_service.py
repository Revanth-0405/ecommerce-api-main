import uuid, json
from datetime import datetime, timezone
from app.models import Product
from app.db import db

ORDERS_FILE = "storage/orders.json"

VALID_STATUS_FLOW = {
    "pending": ["confirmed", "cancelled"],
    "confirmed": ["shipped", "cancelled"],
    "shipped": ["delivered"],
    "delivered": []
}


def load_orders():
    try:
        with open(ORDERS_FILE) as f:
            return json.load(f)
    except Exception:
        return []


def save_orders(data):
    with open(ORDERS_FILE, "w") as f:
        json.dump(data, f, indent=2)


def create_order(data):

    orders = load_orders()
    items = []
    total = 0

    for i in data["items"]:
        p = db.session.get(Product, i["product_id"])
        qty = i["quantity"]

        if not p:
            return {"error": "Product not found"}, 404

        if p.stock_quantity < qty:
            return {"error": "Insufficient stock"}, 400

        p.stock_quantity -= qty
        total += float(p.price) * qty

        items.append({
            "product_id": p.id,
            "quantity": qty,
            "unit_price": float(p.price)
        })

    db.session.commit()

    order = {
        "order_id": str(uuid.uuid4()),
        "customer_email": data["customer_email"],
        "items": items,
        "total": total,
        "status": "pending",
        "created_at": datetime.now(timezone.utc).isoformat()
    }

    orders.append(order)
    save_orders(orders)

    return order


def update_status(order_id, status):

    if status not in ["pending", "confirmed", "shipped", "delivered", "cancelled"]:
        return {"error": "Invalid status"}, 400

    orders = load_orders()

    for o in orders:
        if o["order_id"] == order_id:

            if status not in VALID_STATUS_FLOW[o["status"]]:
                return {"error": "Invalid status transition"}, 400

            o["status"] = status
            save_orders(orders)
            return o

    return {"error": "Order not found"}, 404


def cancel_order(order_id):

    orders = load_orders()

    for o in orders:
        if o["order_id"] == order_id:

            if o["status"] == "cancelled":
                return {"error": "Already cancelled"}, 400

            for item in o["items"]:
                p = db.session.get(Product, item["product_id"])
                if p:
                    p.stock_quantity += item["quantity"]

            db.session.commit()

            o["status"] = "cancelled"
            save_orders(orders)
            return o

    return {"error": "Order not found"}, 404
