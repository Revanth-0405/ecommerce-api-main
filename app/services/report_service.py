from collections import defaultdict
from flask import jsonify
from app.services.order_service import load_orders
from app.models import Product
from app.db import db


def sales_summary():

    orders = load_orders() or []

    total = 0
    counter = defaultdict(int)

    for o in orders:

        if o.get("status") == "cancelled":
            continue

        total += o.get("total",0)

        for item in o.get("items",[]):
            counter[item["product_id"]] += item["quantity"]

    top = sorted(counter.items(), key=lambda x:x[1], reverse=True)[:5]

    result = []
    for pid, qty in top:
        p = db.session.get(Product, pid)
        result.append({
            "product_id": pid,
            "name": p.name if p else "Unknown",
            "sold": qty
        })

    return jsonify({
        "total_revenue": total,
        "top_products": result
    })


def low_stock(threshold):

    products = Product.query.filter(Product.stock_quantity <= threshold).all()

    return jsonify([
        {
            "id": p.id,
            "name": p.name,
            "stock": p.stock_quantity
        }
        for p in products
    ])
