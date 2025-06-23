from django.db import models
from products.models import Product, Flavor


class StatusChoices(models.TextChoices):
    EM_PREPARACAO = 'em_preparacao', 'Em Preparação'
    AGENDADO = 'agendado', 'Agendado'
    CANCELADO = 'cancelado', 'Cancelado'
    CONCLUIDO = 'concluido', 'Concluído'


class Order(models.Model):
    customer_name = models.CharField(max_length=100)
    order_num = models.CharField(
        max_length=50, verbose_name="Número do Pedido", null=True, blank=True
    )
    external_code = models.CharField(
        max_length=50, unique=True, verbose_name="Código Externo", null=True, blank=True
    )
    status = models.CharField(
        max_length=20,
        choices=StatusChoices.choices,
        null=True,
        blank=True,
    )
    delivery_date = models.DateField(verbose_name="Data Agndada")
    delivery_time = models.CharField(verbose_name="Horário agendado")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Criado em")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Atualizado em")

    def __str__(self):
        return f"Order {self.id} by {self.customer_name}"

    class Meta:
        verbose_name = "Pedido"
        verbose_name_plural = "Pedidos"
        ordering = ["-delivery_date"]


class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name="items", on_delete=models.CASCADE)
    quantity = models.FloatField(verbose_name="Quantidade", default=1)
    product = models.ForeignKey(
        Product,
        related_name="order_items",
        on_delete=models.CASCADE,
        null=False,
        blank=False,
        verbose_name="Produto"
    )

    class Meta:
        verbose_name = "Item do Pedido"
        verbose_name_plural = "Itens do Pedido"
        ordering = ["order", "product"]

    def __str__(self):
        return f"Product: {self.product.name if self.product else 'N/A'}"


class OrderItemFlavor(models.Model):
    order_item = models.ForeignKey(
        OrderItem, related_name="flavors", on_delete=models.PROTECT
    )
    flavor = models.ForeignKey(
        Flavor, related_name="order_item_flavors", on_delete=models.PROTECT
    )
    quantity = models.PositiveIntegerField(verbose_name="Quantidade Sabor", default=1)

    class Meta:
        verbose_name = "Sabor do Item do Pedido"
        verbose_name_plural = "Sabores do Item do Pedido"
        ordering = ["order_item", "flavor"]
        unique_together = ("order_item", "flavor")

    def __str__(self):
        return f"Flavor: {self.flavor.name if self.flavor else 'N/A'}"


class ExternalProduct(models.Model):
    ext_product_code = models.CharField(
        max_length=255,
        verbose_name="Código do produto externo",
        null=False,
        blank=False,
    )
    ext_addon_code = models.CharField(
        max_length=255, verbose_name="Código do Adicional", null=False, blank=False
    )
    ext_selection_code = models.CharField(
        max_length=255, verbose_name="Código da Seleção", null=False, blank=False
    )

    product = models.ForeignKey(
        Product,
        related_name="translations",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name="Produto",
    )
    flavor = models.ForeignKey(
        Flavor,
        related_name="translations",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name="Sabor",
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Criado em")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Atualizado em")

    # def __str__(self):
    #    return f"ExternalProduct {self.ext_product_code} to {self.product}"

    class Meta:
        verbose_name = "Tradução de Produto"
        verbose_name_plural = "Tradução de Produtos"
        ordering = ["ext_product_code", "ext_addon_code", "ext_selection_code"]
