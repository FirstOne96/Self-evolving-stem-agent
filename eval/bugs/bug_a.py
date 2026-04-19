# A small e-commerce cart system.
# add_item should add an item dict to the cart.
# get_total should return the sum of price * quantity for all items.
# apply_discount should return total after subtracting discount percent.

DEFAULT_ITEM = {"name": "", "price": 0.0, "quantity": 1}

def add_item(cart, name, price, quantity=1):
    item = DEFAULT_ITEM  # BUG: reuses the same dict object every call
    item["name"] = name
    item["price"] = price
    item["quantity"] = quantity
    cart.append(item)

def get_total(cart):
    return sum(item["price"] * item["quantity"] for item in cart)

def apply_discount(total, discount_percent):
    return total * (1 - discount_percent / 100)
