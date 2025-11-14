"""
Patrón BUILDER para construir órdenes complejas paso a paso
"""
from apps.orders.models import Order, OrderItem
from apps.menu.models import Product


class OrderBuilder:
    """
    Builder para construir órdenes paso a paso.
    """

    def __init__(self):
        self.reset()

    def set_customer(self, customer):
        self._customer = customer
        return self

    def set_mesero(self, mesero):
        self._mesero = mesero
        return self

    def set_table(self, table_number):
        self._table_number = table_number
        return self

    def add_product(self, product_id, quantity=1, extras=None):
        """
        Agregar un producto a la orden.
        """
        if extras is None:
            extras = {}

        # Asegurar que los IDs siempre sean int (por Postman llegan como string)
        product_id = int(product_id)

        self._items.append({
            'product_id': product_id,
            'quantity': int(quantity),
            'extras': extras
        })
        return self

    def add_special_instructions(self, instructions):
        self._special_instructions = instructions
        return self

    def build(self):
        """
        Construye la orden final y la retorna.
        """
        if not self._customer:
            raise ValueError("Cliente requerido para crear la orden")

        if not self._items:
            raise ValueError("La orden debe tener al menos un producto")

        # Crear orden base
        order = Order.objects.create(
            customer=self._customer,
            mesero=self._mesero,
            table_number=self._table_number,
            special_instructions=self._special_instructions
        )

        # Crear cada item
        for item_data in self._items:
            product = Product.objects.get(id=item_data['product_id'])

            order_item = OrderItem.objects.create(
                order=order,
                product=product,
                quantity=item_data['quantity'],
                extras=item_data['extras']
            )

            # Calcular subtotal
            order_item.calculate_subtotal()
            order_item.save()

        # Calcular total de la orden
        order.calculate_total()
        order.save()

        # Preparar builder para una nueva orden
        self.reset()

        return order

    def reset(self):
        """
        Restaura el estado interno del builder.
        """
        self._customer = None
        self._mesero = None
        self._table_number = 1
        self._items = []
        self._special_instructions = ""
        return self


class OrderDirector:
    """
    Director que orquesta secuencias de construcción predefinidas.
    """

    def __init__(self, builder: OrderBuilder):
        self._builder = builder

    def build_simple_order(self, customer, table, product_id):
        return (self._builder
                .set_customer(customer)
                .set_table(table)
                .add_product(product_id)
                .build())

    def build_breakfast_order(self, customer, table, mesero, beverage_id, food_id):
        return (self._builder
                .set_customer(customer)
                .set_table(table)
                .set_mesero(mesero)
                .add_product(beverage_id, extras={"leche": True})
                .add_product(food_id)
                .add_special_instructions("Desayuno")
                .build())

    def build_takeaway_order(self, customer, *product_ids):
        self._builder.set_customer(customer).set_table(0)

        for pid in product_ids:
            self._builder.add_product(pid)

        return (self._builder
                .add_special_instructions("PARA LLEVAR")
                .build())
