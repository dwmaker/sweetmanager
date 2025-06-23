from django.contrib import admin
from django import forms
from products.models import Flavor, Product
from orders.models import Order, OrderItem
from orders.models import ExternalProduct
from orders.models import OrderItemFlavor


class OrderItemFlavorInlineForm(forms.ModelForm):

    class Meta:
        model = OrderItemFlavor
        fields = "__all__"


class OrderItemFlavorInline(admin.TabularInline):
    model = OrderItemFlavor
    extra = 0
    min_num = 1
    form = OrderItemFlavorInlineForm
    fields = ("flavor", "quantity")


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = (
        "order",
        "product",
    )
    search_fields = (
        "order",
        "product",
    )

    ordering = (
        "order",
        "product",
    )
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "order",
                    "product",
                )
            },
        ),
    )
    inlines = [OrderItemFlavorInline]


@admin.register(ExternalProduct)
class ExternalProductAdmin(admin.ModelAdmin):
    readonly_fields = (
        "ext_product_code",
        "ext_addon_code",
        "ext_selection_code"
        )
    search_fields = (
        "ext_product_code",
        "ext_addon_code",
        "ext_selection_code"
        )
    list_display = (
        "ext_product_code",
        "ext_addon_code",
        "ext_selection_code",
        "product",
        "flavor",
        )
    # list_editable=('product', 'flavor')
    list_filter = ("ext_product_code", "product", "flavor")


class OrderItemInlineForm(forms.ModelForm):
    class Meta:
        model = OrderItem
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        product = None
        if "product" in self.data:
            try:
                product_id = int(self.data.get("product"))
                product = Product.objects.get(pk=product_id)
            except (ValueError, TypeError, Product.DoesNotExist):
                pass
        elif self.instance.pk and self.instance.product:
            product = self.instance.product

        if product:
            qs = Flavor.objects.filter(category=product.category)
        else:
            qs = Flavor.objects.none()

        for i in range(1, 6):
            try:
                self.fields[f"flavor_{i}"].queryset = qs
            except KeyError:
                pass


class OrderItemInline(admin.StackedInline):
    model = OrderItem
    extra = 0
    min_num = 1
    form = OrderItemInlineForm
    fields = ("product",)


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        "customer_name",
        "external_code",
        "order_num",
        "status",
        "delivery_date",
        "delivery_time",
    )
    search_fields = (
        "customer_name",
        "order_num",
    )
    list_filter = (
        "delivery_date",
        "delivery_time",
        "status",
    )
    ordering = (
        "delivery_date",
        "delivery_time",
    )
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "customer_name",
                    "status",
                    "external_code",
                    "order_num",
                    "delivery_date",
                    "delivery_time",
                )
            },
        ),
    )
    inlines = [OrderItemInline]
