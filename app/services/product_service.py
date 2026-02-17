from app.models import Product
from app.db import db


def create_product(data):
    product = Product(**data)
    db.session.add(product)
    db.session.commit()
    return product
