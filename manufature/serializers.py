# sua_app/serializers.py
from rest_framework import serializers
from .models import Order, OrderItem


# Serializador para a entidade filho (OrderItem)
class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ["id", "product_name", "quantity", "unit_price", "get_total"]


# Serializador principal para Order, incluindo OrderItem aninhado
class OrderSerializer(serializers.ModelSerializer):
    # O nome 'items' corresponde ao related_name do ForeignKey em OrderItem
    items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = ["id", "customer_name", "created_at", "notes", "items"]
