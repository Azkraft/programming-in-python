# Баг: нарушение контракта a == b  =>  hash(a) == hash(b)
class Product_broken:
    def __init__(self, sku, price):
        self.sku, self.price = sku, price

    def __eq__(self, other):
        return self.sku == other.sku

    def __hash__(self):
        return hash(self.price)


p1 = Product_broken("A-1", 100)
p2 = Product_broken("A-1", 200)
stock = {p1: 5}
print(stock.get(p2))   # None, хотя p1 == p2

# Два товара с одинаковым SKU равны по __eq__, но хеш считается по цене.
# При поиске p2 словарь заходит в корзину hash(p2), где записи с хешем hash(100)
# нет, поэтому возвращает None — контракт hash/eq нарушен.

# Исправление: хеш и равенство должны зависеть от одного и того же (неизменяемого) поля.
class Product:
    def __init__(self, sku, price):
        self.sku, self.price = sku, price

    def __eq__(self, other):
        return self.sku == other.sku

    def __hash__(self):
        return hash(self.sku)


p1 = Product("A-1", 100)
p2 = Product("A-1", 200)
stock = {p1: 5}
print(stock.get(p2))   # 5 — ключ находится
