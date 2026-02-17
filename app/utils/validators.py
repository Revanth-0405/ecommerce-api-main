import re

def validate_product(data):

    required=["sku","name","price","stock_quantity","category"]

    for f in required:
        if f not in data:
            return f"{f} required"

    if data["price"]<=0:
        return "Price must be positive"

    if data["stock_quantity"]<0:
        return "Stock cannot be negative"

    if len(data["name"])<2:
        return "Name too short"

    return None


def validate_email(email):
    return re.match(r"[^@]+@[^@]+\.[^@]+",email)
