import re
from typing import List, Dict, Any
import numpy
from rest_framework import serializers
from django.urls import reverse
from django.contrib.contenttypes.models import ContentType
from urllib.parse import urlencode

from orders.models import (
    ExternalProduct,
    Order,
    OrderItem,
    OrderItemFlavor,
    Flavor,
    StatusChoices
    )
from products.models import Product
from django.db.models import Model


def adminurl_changelist(target_class: Model, **kwargs):
    ct = ContentType.objects.get_for_model(target_class)
    r = reverse(f"admin:{ct.app_label}_{ct.model}_changelist") + \
        "?" + urlencode(kwargs)
    return r


def parse_items(message: str) -> List[Dict[str, Any]]:
    lines = message.strip().splitlines()
    result = []
    current_item = None
    current_addon = None
    item_pattern = r"^\d+(\.\d+)?\s*x\s*"
    quantity_pattern = r"(?P<quantity>\d+(?:\.\d+)?)\s*x\s*(?P<name>.+)"
    addon_header_pattern = r"^\s{2,}(?P<addon>[^:]+):\s*$"
    for line in lines:
        line = line.rstrip()
        # Detect top-level item
        if re.match(item_pattern, line):
            match = re.match(quantity_pattern, line)
            if match:
                if current_item:
                    result.append(current_item)
                current_item = {
                    "quantity": float(match.group("quantity")),
                    "ext_product_code": match.group("name"),
                    "addons": [],
                }
                current_addon = None
        # Detect addon header
        elif re.match(addon_header_pattern, line):
            match = re.match(addon_header_pattern, line)
            if match and current_item:
                current_addon = {
                    "ext_addon_code": match.group("addon").strip(),
                    "selection": [],
                }
                current_item["addons"].append(current_addon)
        # Detect addon selection
        elif re.match(r"^\s{4,}\d+(\.\d+)?\s*x\s*", line):
            match = re.match(r"^\s*(\d+(?:\.\d+)?)\s*x\s*(.+)$", line.strip())
            if match and current_addon:
                current_addon["selection"].append(
                    {
                        "ext_selection_code": match.group(2).strip(),
                        "quantity": float(match.group(1)),
                    }
                )

    if current_item:
        result.append(current_item)

    return result


def parse_order_sheet(df):
    # Renomeia as colunas
    df.rename(
        columns={
            "Telefone": "phone_number",
            "Data de criação": "creation_date",
            "Início do preparo": "production_date",
            "Pedido pronto": "is_ready",
            "Pedido fechado": "closed_order",
            "Hora do agendamento": "delivery_time",
            "Total de itens": "items_total",
            "Método de pagamento": "payment_method",
            "Canal": "channel",
            "Taxa de entrega": "delivery_tax",
            "Taxa de serviço": "service_tax",
            "Taxa adicional": "additional_tax",
            "Complemento": "address_complement",
            "Cidade": "address_city",
            "Estado": "address_state",
            "CEP": "address_cep",
            "Acréscimo da maquineta": "additional_machine_tax",
            "Desconto": "discount",
            "Total do pedido": "total",
            "Troco para": "payback",
            "Rua": "street",
            "Número": "number",
            "Bairro": "neighborhood",
        },
        inplace=True,
    )

    df = df.replace(numpy.nan, None)
    df["items"] = df["Produtos"].apply(parse_items)
    df.drop(columns=["Produtos"], inplace=True)
    data = df.to_dict(orient="records")

    return data


class FlavorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Flavor
        fields = ("id", "name")


class OrderItemFlavorSerializer(serializers.ModelSerializer):
    flavor = FlavorSerializer()

    class Meta:
        model = OrderItemFlavor
        fields = ("flavor", "quantity")


class ProductSerializer(serializers.ModelSerializer):

    class Meta:
        model = Product
        fields = (
            "id",
            "name",
            "max_flavor_quantity",
            "min_quantity_per_flavor"
            )


class OrderItemSerializer(serializers.ModelSerializer):
    flavors = OrderItemFlavorSerializer(many=True, read_only=True)

    product = ProductSerializer()

    class Meta:
        model = OrderItem
        fields = ("quantity", "product", "flavors")


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = (
            "id",
            "customer_name",
            "order_num",
            "external_code",
            "delivery_date",
            "delivery_time",
            "items",
        )


def register_external_codes(parsed):
    for ext_order in parsed:
        for ext_order_item in ext_order["items"]:
            ext_product_code = ext_order_item["ext_product_code"]
            for ext_addon in ext_order_item["addons"]:
                ext_addon_code = ext_addon["ext_addon_code"]
                for ext_selection in ext_addon["selection"]:
                    ext_selection_code = ext_selection["ext_selection_code"]
                    external_products = ExternalProduct.objects.filter(
                        ext_product_code=ext_product_code,
                        ext_addon_code=ext_addon_code,
                        ext_selection_code=ext_selection_code,
                    )
                    if len(external_products) == 0:
                        external_product = ExternalProduct(
                            ext_product_code=ext_product_code,
                            ext_addon_code=ext_addon_code,
                            ext_selection_code=ext_selection_code,
                        )
                        external_product.save()
                    else:
                        external_product = external_products[0]


class CustomError(Exception):
    def __init__(self, message, url):
        Exception.__init__(self, message)
        self.url = url


def merge_order(ext_order):
    order = Order.objects.filter(external_code=ext_order["Id do pedido"]) \
        .first()
    if order is None:
        order = Order(external_code=ext_order["Id do pedido"])
    else:

        for order_item in OrderItem.objects.filter(order=order):
            for order_item_flavor in OrderItemFlavor.objects.filter(
                order_item=order_item
            ):
                order_item_flavor.delete()

            order_item.delete()
    order.delivery_date = ext_order["Data do agendamento"].date()
    order.customer_name = ext_order["Cliente"]
    order.order_num = ext_order["Número do pedido"]

    depara_status = {
        "Em preparação": StatusChoices.EM_PREPARACAO,
        "Agendado": StatusChoices.AGENDADO,
        "Cancelado": StatusChoices.CANCELADO,
        "Concluído": StatusChoices.CONCLUIDO,
        }
    order.status = depara_status.get(ext_order["Status"], None)
    order.save()
    for ext_order_item in ext_order["items"]:
        ext_product_code = ext_order_item["ext_product_code"]

        product = None

        for ext_addon in ext_order_item["addons"]:
            ext_addon_code = ext_addon["ext_addon_code"]
            # buscando produto
            for ext_selection in ext_addon["selection"]:
                ext_selection_code = ext_selection["ext_selection_code"]
                external_product = ExternalProduct.objects.filter(
                    ext_product_code=ext_product_code,
                    ext_addon_code=ext_addon_code,
                    ext_selection_code=ext_selection_code,
                    product__isnull=False,
                ).first()
                if external_product:
                    product = external_product.product
        if product is None:
            ct = ContentType.objects.get_for_model(ExternalProduct)
            raise CustomError(
                f"Não foi encontrado produto para {ext_product_code}",
                # TODO: normalizar em util.py
                reverse(f"admin:{ct.app_label}_{ct.model}_changelist") +
                "?" +
                urlencode({'ext_product_code': ext_product_code})
                )
        order_item = OrderItem.objects.create(
            product=product, order=order, quantity=ext_order_item["quantity"]
        )
        # buscando sabor
        for ext_addon in ext_order_item["addons"]:
            ext_addon_code = ext_addon["ext_addon_code"]
            for ext_selection in ext_addon["selection"]:

                ext_selection_code = ext_selection["ext_selection_code"]
                external_flavors = ExternalProduct.objects.filter(
                    ext_product_code=ext_product_code,
                    ext_addon_code=ext_addon_code,
                    ext_selection_code=ext_selection_code,
                    flavor__isnull=False,
                )
                for external_flavor in external_flavors:
                    OrderItemFlavor.objects.create(
                        order_item=order_item,
                        flavor=external_flavor.flavor,
                        quantity=ext_selection["quantity"],
                    )
    return order


def loadxls_order_service(df):
    parsed = parse_order_sheet(df)
    register_external_codes(parsed)
    orders = []
    errors = []
    for ext_order in parsed:
        try:
            order = merge_order(ext_order)
            orders.append(order)
        except CustomError as e:
            errors.append({"message": e.__str__(), "url": e.url})
    serialized_orders = list(map(
        lambda order: OrderSerializer(order).data,
        orders
        ))
    return {
        "parsed": parsed,
        "orders": serialized_orders,
        "created": {},
        "errors": errors
        }
