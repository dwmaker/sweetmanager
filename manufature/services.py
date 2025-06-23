from datetime import date, datetime
import pandas as pd
from rest_framework import serializers
from products.models import Product, Flavor, Category, ProductDataSheetRecipe
from orders.models import Order, OrderItem, OrderItemFlavor


def normalize_measure(value: float, measure_code: str) -> float:
    print("TODO: implementar código")
    return value


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ("id", "name")


class ProductSerializer(serializers.ModelSerializer):
    category = CategorySerializer()

    class Meta:
        model = Product
        fields = (
            "id",
            "name",
            "max_flavor_quantity",
            "min_quantity_per_flavor",
            "category",
        )


class FlavorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Flavor
        fields = ("id", "name", "category")


class OrderItemFlavorSerializer(serializers.ModelSerializer):
    flavor = FlavorSerializer()

    class Meta:
        model = OrderItemFlavor
        fields = ("id", "quantity", "flavor")


class OrderItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer()
    flavors = OrderItemFlavorSerializer(many=True, read_only=True)

    class Meta:
        model = OrderItem
        fields = "__all__"


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = (
            "id",
            "customer_name",
            "external_code",
            "delivery_date",
            "delivery_time",
            "created_at",
            "updated_at",
            "items",
        )


def serialize_dataframe(df_merged) -> list[dict]:
    if df_merged is None:
        return None
    rows = df_merged.reset_index(drop=True).to_dict(
        orient="records",
    )
    # for row in rows:
    #    for k in row:
    #        try:
    #            if np.isnan(row[k]):
    #                row[k] = None
    #        except TypeError:
    #            pass
    return rows


def create_report(begin_date: date, end_date: date, status_list):
    df_recipes_by_bakingpan = None
    res_recipe_by_category = []

    begin_datetime = datetime(
        year=begin_date.year,
        month=begin_date.month,
        day=begin_date.day,
        hour=23,
        minute=59,
        second=59,
        microsecond=999999,
        # tzinfo=pytz.UTC,
    )
    end_datetime = datetime(
        year=end_date.year,
        month=end_date.month,
        day=end_date.day,
        hour=23,
        minute=59,
        second=59,
        microsecond=999999,
        # tzinfo=end_date.tzinfo,
        # tzinfo=pytz.UTC,
    )
    orders = Order.objects.filter(
        delivery_date__gte=begin_datetime,
        delivery_date__lte=end_datetime,
        status__in=status_list,
    )
    orders = OrderSerializer(orders, many=True).data
    res_messages = []
    res_orders = OrderItemFlavor.objects.filter(
        order_item__order__delivery_date__gte=begin_datetime,
        order_item__order__delivery_date__lte=end_datetime,
        order_item__order__status__in=status_list,
    ).values(
        "order_item__product__id",
        "order_item__product__name",
        "order_item__product__category__id",
        "order_item__product__category__name",
        "flavor__id",
        "flavor__name",
        "quantity",
        "order_item__product__max_flavor_quantity",
    )
    if len(res_orders) > 0:

        df_orders = pd.DataFrame(res_orders)
        # Executando renomeação, exclusão e cálculo em um único comando

        df_orders["orders_quantity"] = (
            df_orders["quantity"]
            / df_orders["order_item__product__max_flavor_quantity"]
        )
        df_orders["orders_product_id"] = df_orders["order_item__product__id"]
        df_orders["orders_product_name"] = df_orders["order_item__product__name"]
        df_orders["orders_flavor_id"] = df_orders["flavor__id"]
        df_orders["orders_category_id"] = df_orders["order_item__product__category__id"]
        df_orders["orders_category_name"] = df_orders[
            "order_item__product__category__name"
        ]
        df_orders["orders_flavor_name"] = df_orders["flavor__name"]
        df_orders = df_orders[
            [
                "orders_quantity",
                "orders_product_id",
                "orders_product_name",
                "orders_flavor_id",
                "orders_category_id",
                "orders_category_name",
                "orders_flavor_name",
            ]
        ]

        res_datasheet = ProductDataSheetRecipe.objects.filter().values(
            "data_sheet_id",
            "id",
            "multiple",
            "measure_quantity",
            "measure_unit",
            "recipe__id",
            "recipe__name",
            "recipe__measure_unit",
            "recipe__measure_quantity",
            "recipe__recipe_category__id",
            "recipe__recipe_category__name",
            "data_sheet__product__id",
            "data_sheet__product__name",
            "data_sheet__flavor__id",
            "data_sheet__flavor__name",
            "baking_pan__id",
            "baking_pan__name",
        )

        df_datasheet = pd.DataFrame(res_datasheet)
        df_datasheet["datasheet_id"] = df_datasheet["data_sheet_id"]
        df_datasheet["datasheet_multiple"] = df_datasheet["multiple"]
        df_datasheet["datasheet_recipe_id"] = df_datasheet["recipe__id"]
        df_datasheet["datasheet_recipe_name"] = df_datasheet["recipe__name"]
        df_datasheet["datasheet_recipe_category_id"] = df_datasheet[
            "recipe__recipe_category__id"
        ]
        df_datasheet["datasheet_recipe_category_name"] = df_datasheet[
            "recipe__recipe_category__name"
        ]
        df_datasheet["datasheet_product_id"] = df_datasheet["data_sheet__product__id"]
        df_datasheet["datasheet_product_name"] = df_datasheet[
            "data_sheet__product__name"
        ]
        df_datasheet["datasheet_flavor_id"] = df_datasheet["data_sheet__flavor__id"]
        df_datasheet["datasheet_flavor_name"] = df_datasheet["data_sheet__flavor__name"]
        df_datasheet["datasheet_bakingpan_id"] = df_datasheet["baking_pan__id"]
        df_datasheet["datasheet_bakingpan_name"] = df_datasheet["baking_pan__name"]

        df_datasheet["datasheet_weigth"] = df_datasheet.apply(
            lambda row: normalize_measure(
                row["measure_quantity"], row["measure_unit"]
            ),
            axis=1,
        )
        df_datasheet["datasheet_recipe_weigth"] = df_datasheet.apply(
            lambda row: normalize_measure(
                row["recipe__measure_quantity"], row["recipe__measure_unit"]
            ),
            axis=1,
        )
        df_datasheet["datasheet_recipe_count"] = (
            df_datasheet["datasheet_multiple"] / df_datasheet["datasheet_recipe_weigth"]
        )

        df_datasheet = df_datasheet[
            [
                "datasheet_product_id",
                "datasheet_flavor_id",
                "datasheet_id",
                "datasheet_multiple",
                "datasheet_weigth",
                "datasheet_recipe_weigth",
                "datasheet_recipe_id",
                "datasheet_recipe_name",
                "datasheet_recipe_category_id",
                "datasheet_recipe_category_name",
                "datasheet_bakingpan_id",
                "datasheet_bakingpan_name",
            ]
        ]

        df_merged = df_orders.merge(
            df_datasheet,
            left_on=["orders_product_id", "orders_flavor_id"],
            right_on=[
                "datasheet_product_id",
                "datasheet_flavor_id",
            ],
            how="left",
        ).reset_index()

        df_messages = df_merged[df_merged["datasheet_product_id"].isna()][
            [
                "orders_product_id",
                "orders_product_name",
                "orders_flavor_id",
                "orders_category_id",
                "orders_category_name",
                "orders_flavor_name",
            ]
        ]

        df_messages["detail"] = df_messages.apply((
            "Ficha técnica não encontrada para " +
            "categoria: {orders_category_name}, " +
            "produto:{orders_product_name}, " +
            "sabor:{orders_flavor_name}").format_map,
            axis=1,
        )
        df_messages["type"] = "warning"
        df_messages["url"] = df_messages.apply(
            # TODO: normalizar em util.py
            "/admin/products/productdatasheet/add/?product={orders_product_id}&flavor={orders_flavor_id}".format_map,
            axis=1,
        )
        df_messages = df_messages[["detail", "type", "url"]]
        res_messages = res_messages + serialize_dataframe(df_messages)

        df_recipe_by_category = df_merged[
            [
                "datasheet_recipe_category_id",
                "datasheet_recipe_category_name",
                "datasheet_recipe_id",
                "datasheet_recipe_name",
                "orders_quantity",
                "datasheet_multiple",
                "datasheet_weigth",
                "datasheet_recipe_weigth",
            ]
        ]

        df_merged = df_merged[df_merged["datasheet_product_id"].notna()]

        df_recipe_by_category["production_weight"] = (
            df_recipe_by_category["orders_quantity"]
            * df_recipe_by_category["datasheet_multiple"]
            * df_recipe_by_category["datasheet_weigth"]
        )
        df_recipe_by_category["recipe_count"] = (
            df_recipe_by_category["production_weight"]
            / df_recipe_by_category["datasheet_recipe_weigth"]
        )

        df_recipe_by_category = df_recipe_by_category[
            [
                "datasheet_recipe_category_id",
                "datasheet_recipe_category_name",
                "datasheet_recipe_id",
                "datasheet_recipe_name",
                "production_weight",
                "recipe_count",
            ]
        ].reset_index()

        df_recipe_by_category = (
            df_recipe_by_category.groupby(
                [
                    "datasheet_recipe_category_id",
                    "datasheet_recipe_category_name",
                    "datasheet_recipe_id",
                    "datasheet_recipe_name",
                ]
            )
            .agg(
                sum_production_weight=("production_weight", "sum"),
                sum_recipe_count=("recipe_count", "sum"),
            )
            .reset_index()
        )
        for category_name, group in df_recipe_by_category.groupby(
            ["datasheet_recipe_category_id", "datasheet_recipe_category_name"]
        ):
            category_id, category_name = category_name

            items = []
            for _, row in group.iterrows():
                items.append(
                    {
                        "datasheet_recipe_id": row["datasheet_recipe_id"],
                        "datasheet_recipe_name": row["datasheet_recipe_name"],
                        "production_weight": row["sum_production_weight"],
                        "recipe_count": row["sum_recipe_count"],
                    }
                )

            res_recipe_by_category.append(
                {
                    "datasheet_recipe_category_id": category_id,
                    "datasheet_recipe_category_name": category_name,
                    "items": items,
                }
            )

        ##################################################################
        df_recipes_by_bakingpan = df_merged
        df_recipes_by_bakingpan = df_recipes_by_bakingpan[
            df_recipes_by_bakingpan["datasheet_bakingpan_id"].notnull()
        ]

        df_recipes_by_bakingpan["production_quantity"] = (
            df_recipes_by_bakingpan["orders_quantity"]
            * df_recipes_by_bakingpan["datasheet_multiple"]
        )
        df_recipes_by_bakingpan["production_weigth"] = (
            df_recipes_by_bakingpan["production_quantity"]
            * df_recipes_by_bakingpan["datasheet_weigth"]
        )

        df_recipes_by_bakingpan = (
            df_recipes_by_bakingpan.groupby(
                [
                    "datasheet_recipe_id",
                    "datasheet_recipe_name",
                    "datasheet_bakingpan_id",
                    "datasheet_bakingpan_name",
                    "datasheet_weigth",
                ]
            )
            .agg(
                sum_production_weigth=("production_weigth", "sum"),
                sum_production_quantity=("production_quantity", "sum"),
            )
            .reset_index()
        )

    Y_B_D = '%Y-%b-%d'
    D_B = '%d/%b'
    Y = '%Y'
    D = '%d'
    B_Y = '%b/%y'
    if begin_date.year != end_date.year:
        period_range = f"{begin_date.strftime(Y_B_D)} ~ {end_date.strftime(Y_B_D)}"
    elif begin_date.month != end_date.month:
        period_range = f"{begin_date.strftime(D_B)} ~ {end_date.strftime(D_B)} de {end_date.strftime(Y)}"
    else:
        period_range = f"{begin_date.strftime(D)} ~ {end_date.strftime(D)} de {end_date.strftime(B_Y)}"

    return {
        "title": f"Produção de {period_range}",
        "company_name": "Dolce Stupendo",
        "generation_date": datetime.now(),
        "orders": orders,
        # "df_datasheet": serialize_dataframe(df_datasheet),
        # "df_orders": serialize_dataframe(df_orders),
        "recipes_by_bakingpan": serialize_dataframe(df_recipes_by_bakingpan),
        "recipe_by_category": res_recipe_by_category,
        "messages": res_messages,
    }
