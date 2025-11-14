"""
Modelos para órdenes
"""
from django.db import models
from apps.users.models import User
from apps.menu.models import Product
from decimal import Decimal


class Order(models.Model):
    """
    Orden de pedido
    Gestiona estados mediante State Pattern
    """

    STATUS_CHOICES = [
        ('PENDIENTE', 'Pendiente'),
        ('EN_PREPARACION', 'En Preparación'),
        ('LISTO', 'Listo'),
        ('ENTREGADO', 'Entregado'),
        ('CANCELADO', 'Cancelado'),
    ]

    customer = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='orders'
    )
    mesero = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_orders'
    )

    table_number = models.IntegerField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDIENTE')
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    special_instructions = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    prepared_at = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'orders'
        verbose_name = 'Orden'
        verbose_name_plural = 'Órdenes'
        ordering = ['-created_at']

    def __str__(self):
        return f"Orden #{self.id} - Mesa {self.table_number} - {self.status}"

    def calculate_total(self):
        """Calcular total de la orden"""
        total = sum(item.subtotal for item in self.items.all())
        self.total_price = total
        self.save()
        return total

    def can_advance(self):
        """Verificar si la orden puede avanzar al siguiente estado"""
        transitions = {
            'PENDIENTE': True,
            'EN_PREPARACION': True,
            'LISTO': True,
            'ENTREGADO': False,
            'CANCELADO': False,
        }
        return transitions.get(self.status, False)

    def can_cancel(self):
        """Verificar si la orden puede ser cancelada"""
        return self.status in ['PENDIENTE', 'EN_PREPARACION']


class OrderItem(models.Model):
    """Item individual de una orden"""

    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)

    # DECORATOR: extras aplicados
    extras = models.JSONField(default=dict, help_text="Extras seleccionados: {'extra': True}")
    extras_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    class Meta:
        db_table = 'order_items'
        verbose_name = 'Item de Orden'
        verbose_name_plural = 'Items de Órdenes'

    def __str__(self):
        return f"{self.quantity}x {self.product.name}"

    def save(self, *args, **kwargs):
        # Asegurar precio base
        if self.unit_price is None:
            self.unit_price = self.product.base_price or Decimal('0.00')

        # Asegurar extras
        extras_price = self.product.get_extras_price(self.extras or {}) or Decimal('0.00')
        self.extras_price = extras_price

        # Calcular subtotal
        self.subtotal = (self.unit_price + extras_price) * self.quantity

        super().save(*args, **kwargs)

    def calculate_subtotal(self):
        """Calcular subtotal del item"""
        self.extras_price = self.product.get_extras_price(self.extras)
        self.subtotal = (self.unit_price + self.extras_price) * self.quantity
        self.save()
        return self.subtotal


class OrderHistory(models.Model):
    """
    Historial de cambios de orden (para Command Pattern)
    """

    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='history')
    action = models.CharField(max_length=50)
    previous_status = models.CharField(max_length=20, blank=True)
    new_status = models.CharField(max_length=20, blank=True)
    changed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    reason = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'order_history'
        verbose_name = 'Historial de Orden'
        verbose_name_plural = 'Historiales de Órdenes'
        ordering = ['-timestamp']

    def __str__(self):
        return f"Orden #{self.order.id} - {self.action} - {self.timestamp}"