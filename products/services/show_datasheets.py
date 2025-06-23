from rest_framework import serializers
from products.models import (
    ProductDataSheet,
    ProductDataSheetRecipe,
)


class ProductDataSheetRecipeSerializer(serializers.ModelSerializer):
    baking_pan = serializers.SerializerMethodField()
    recipe = serializers.SerializerMethodField()

    def get_baking_pan(self, obj: ProductDataSheetRecipe):
        return None if obj.baking_pan is None else obj.baking_pan.name

    def get_recipe(self, obj: ProductDataSheetRecipe):
        return None if obj.recipe is None else obj.recipe.name

    class Meta:
        model = ProductDataSheetRecipe
        exclude = ["data_sheet"]


class ProductDataSheetSerializer(serializers.ModelSerializer):
    product = serializers.SerializerMethodField()
    flavor = serializers.SerializerMethodField()

    def get_flavor(self, obj: ProductDataSheet):
        return None if obj.flavor is None else obj.flavor.name

    def get_product(self, obj: ProductDataSheet):
        return None if obj.product is None else obj.product.name

    recipes = ProductDataSheetRecipeSerializer(many=True, read_only=True)

    class Meta:
        model = ProductDataSheet
        exclude = ["created_at", "updated_at"]


def show_datasheets():
    datasheets = ProductDataSheet.objects.all()
    return ProductDataSheetSerializer(datasheets, many=True, read_only=True) \
        .data
