from catalog.models import Product

CART_SESSION_KEY = "cart"


class Cart:
    def __init__(self, request):
        self.session = request.session
        cart = self.session.get(CART_SESSION_KEY)
        if cart is None:
            cart = self.session[CART_SESSION_KEY] = {}
        self.cart = cart

    def add(self, product, quantity=1):
        key = str(product.id)
        if key not in self.cart:
            self.cart[key] = {
                "id": product.id,
                "name": product.name,
                "price": str(product.price),
                "quantity": 0,
                "image": product.image.url if product.image else None,
                "slug": product.slug,
            }
        self.cart[key]["quantity"] += quantity
        self._save()

    def remove(self, product_id):
        key = str(product_id)
        if key in self.cart:
            del self.cart[key]
            self._save()

    def update(self, product_id, quantity):
        key = str(product_id)
        if key in self.cart:
            if quantity > 0:
                self.cart[key]["quantity"] = quantity
            else:
                del self.cart[key]
            self._save()

    def clear(self):
        self.session[CART_SESSION_KEY] = {}
        self._save()

    def _save(self):
        self.session.modified = True

    def __iter__(self):
        for item in self.cart.values():
            yield {
                **item,
                "total": float(item["price"]) * item["quantity"],
            }

    def __len__(self):
        return sum(item["quantity"] for item in self.cart.values())

    @property
    def total_price(self):
        return sum(float(item["price"]) * item["quantity"] for item in self.cart.values())
