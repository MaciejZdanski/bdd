class Product:
    def __init__(self, name, price, description, stock, status):
        self.name = name
        self.price = price
        self.description = description
        self.stock = stock
        self.status = status

    def to_dict(self):
        return {
            "name": self.name,
            "price": self.price,
            "description": self.description,
            "stock": self.stock,
            "status": self.status  
        }
