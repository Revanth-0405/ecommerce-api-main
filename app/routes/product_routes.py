from flask import Blueprint,request,jsonify
from app.middleware import require_api_key
from app.services.product_service import create_product
from app.utils.validators import validate_product
from app.utils import error_response
from app.models import Product
from app.db import db

product_bp=Blueprint("product",__name__)


@product_bp.route("/api/v1/products",methods=["POST"])
@require_api_key("admin")
def create():

    data=request.get_json(silent=True)

    if not data:
        return error_response("Invalid JSON","PROD001",400)

    err=validate_product(data)
    if err:
        return error_response(err,"PROD002",400)

    p=create_product(data)
    return jsonify({"id":p.id}),201


@product_bp.route("/api/v1/products")
@require_api_key()
def list_products():

    include=request.args.get("include_inactive")=="true"
    q=Product.query if include else Product.query.filter_by(is_active=True)

    category=request.args.get("category")
    minp=request.args.get("min_price",type=float)
    maxp=request.args.get("max_price",type=float)

    if category:
        q=q.filter(Product.category==category)
    if minp is not None:
        q=q.filter(Product.price>=minp)
    if maxp is not None:
        q=q.filter(Product.price<=maxp)

    return jsonify([
        {
            "id":p.id,
            "name":p.name,
            "price":float(p.price),
            "stock":p.stock_quantity
        } for p in q.all()
    ])


@product_bp.route("/api/v1/products/<int:pid>",methods=["PUT"])
@require_api_key("admin")
def update_product(pid):

    p=Product.query.get(pid)
    if not p:
        return error_response("Not found","PROD404",404)

    data=request.json
    allowed={"name","price","stock_quantity","category","description"}

    for k,v in data.items():
        if k in allowed:
            setattr(p,k,v)

    db.session.commit()
    return jsonify({"message":"updated"})


@product_bp.route("/api/v1/products/<int:pid>",methods=["DELETE"])
@require_api_key("admin")
def delete_product(pid):

    p=Product.query.get(pid)
    if not p:
        return error_response("Not found","PROD404",404)

    p.is_active=False
    db.session.commit()
    return jsonify({"message":"deleted"})


@product_bp.route("/api/v1/products/<int:pid>/stock",methods=["PATCH"])
@require_api_key("admin")
def adjust_stock(pid):

    p=Product.query.get(pid)
    if not p:
        return error_response("Not found","PROD404",404)

    adj=request.json.get("adjust",0)

    if p.stock_quantity+adj<0:
        return error_response("Stock cannot be negative","PROD400",400)

    p.stock_quantity+=adj
    db.session.commit()

    return jsonify({"stock":p.stock_quantity})
