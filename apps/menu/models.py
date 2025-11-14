"""
Modelos para menú - Patrones COMPOSITE y DECORATOR
"""
from django.db import models
from decimal import Decimal


class Category(models.Model):
    """
    Categoría de menú - Componente COMPOSITE
    Representa nodos del árbol de menú
    """

    CATEGORY_TYPES = [
        ('BEBIDAS', 'Bebidas'),
        ('ENTRADAS', 'Entradas'),
        ('COMIDAS', 'Comidas'),
        ('POSTRES', 'Postres'),
    ]

    name = models.CharField(max_length=100)
    category_type = models.CharField(max_length=20, choices=CATEGORY_TYPES)
    description = models.TextField(blank=True)
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='subcategories'
    )
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'menu_categories'
        verbose_name = 'Categoría'
        verbose_name_plural = 'Categorías'
        ordering = ['category_type', 'name']

    def __str__(self):
        return self.name

    def get_all_products(self):
        """
        COMPOSITE: Obtener todos los productos de esta categoría
        y sus subcategorías recursivamente
        """
        products = list(self.products.filter(is_available=True))

        for subcategory in self.subcategories.filter(is_active=True):
            products.extend(subcategory.get_all_products())

        return products

    def get_total_price(self):
        """COMPOSITE: Calcular precio total de todos los productos"""
        total = sum(p.base_price for p in self.get_all_products())
        return total


class Product(models.Model):
    """
    Producto base del menú
    Soporta DECORATOR mediante extras configurables
    """

    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name='products'
    )
    name = models.CharField(max_length=200)
    description = models.TextField()
    base_price = models.DecimalField(max_digits=10, decimal_places=2)
    preparation_time = models.IntegerField(help_text="Tiempo en minutos")
    is_available = models.BooleanField(default=True)

    # DECORATOR: extras disponibles como JSON
    # Ejemplo: {"leche": 0.5, "azucar": 0.0, "extra_shot": 1.0}
    available_extras = models.JSONField(
        default=dict,
        help_text="Extras disponibles y sus precios: {'extra_name': precio}"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'menu_products'
        verbose_name = 'Producto'
        verbose_name_plural = 'Productos'
        ordering = ['category', 'name']

    def __str__(self):
        return f"{self.name} - ${self.base_price}"

    def calculate_price_with_extras(self, extras):
        """
        DECORATOR: Calcular precio con extras aplicados

        Args:
            extras: dict {'extra_name': True/False}

        Returns:
            Decimal con precio total
        """
        total = self.base_price

        for extra_name, selected in extras.items():
            if selected and extra_name in self.available_extras:
                total += Decimal(str(self.available_extras[extra_name]))

        return total

    def get_extras_price(self, extras):
        """
        Calcula el precio de los extras.
        Si no hay extras, devuelve 0.00 en lugar de None.
        """
        if not extras:
            return Decimal('0.00')

        total = Decimal('0.00')

        # ejemplo: cada extra suma +0.50
        for key, value in extras.items():
            if value:
                total += Decimal('0.50')

        return total


class ProductDecorator:
    """
    DECORATOR abstracto para agregar funcionalidad a productos
    (Opcional - implementación explícita del patrón)
    """

    def __init__(self, product):
        self._product = product

    def get_name(self):
        return self._product.name

    def get_price(self):
        return self._product.base_price

    def get_description(self):
        return self._product.description


class ExtraDecorator(ProductDecorator):
    """
    Decorador concreto para agregar extras
    """

    def __init__(self, product, extra_name, extra_price):
        super().__init__(product)
        self.extra_name = extra_name
        self.extra_price = Decimal(str(extra_price))

    def get_name(self):
        return f"{self._product.name} + {self.extra_name}"

    def get_price(self):
        return self._product.base_price + self.extra_price

    def get_description(self):
        return f"{self._product.description} (con {self.extra_name})"