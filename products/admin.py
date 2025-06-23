

from django.contrib import admin
from django.template.response import TemplateResponse
from datetime import datetime
from django import forms

from products.models import (
    RecipeStep,
    Product,
    ProductDataSheet,
    ProductDataSheetRecipe,
    Category,
    Flavor,
    Recipe,
    RecipeIngredient,
    Ingredient,
    BakingPan,
    ProductionItem,
    RecipeCategory,
    ProductionBatch
)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "description")
    ordering = ("name",)


@admin.register(BakingPan)
class BakingPanAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "description",
    )
    search_fields = (
        "name",
        "description",
    )
    ordering = ("name",)
    fieldsets = ((None, {"fields": ("name", "description")}),)


@admin.register(Flavor)
class FlavorAdmin(admin.ModelAdmin):
    list_display = ("name", "description", "category", "is_active")
    search_fields = ("name", "description")
    list_filter = ("category", "is_active")
    ordering = (
        "category",
        "name",
    )
    fieldsets = ((None, {"fields": (
        "name",
        "description",
        "category",
        "is_active"
        )}),)


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "description",
    )
    search_fields = (
        "name",
        "description",
    )
    ordering = ("name",)
    fieldsets = ((None, {"fields": ("name", "description")}),)


class ProductAdminForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = "__all__"
        widgets = {
            "flavors": forms.CheckboxSelectMultiple,
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Inicialmente, sem categoria definida, mostra todos os sabores
        if "category" in self.data:
            try:
                category_id = int(self.data.get("category"))
                self.fields["flavors"].queryset = Flavor.objects.filter(
                    category_id=category_id
                )
            except (ValueError, TypeError):
                self.fields["flavors"].queryset = Flavor.objects.none()
        elif self.instance.pk and self.instance.category:
            self.fields["flavors"].queryset = Flavor.objects.filter(
                category=self.instance.category
            )
        else:
            self.fields["flavors"].queryset = Flavor.objects.none()


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "is_active")  # , 'image'
    search_fields = ("name", "category__name")
    list_filter = ("category", "is_active")
    ordering = ("category",)
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "name",
                    "description",
                    "category",
                    "is_active",
                    "flavors",
                    "max_flavor_quantity",
                    "min_quantity_per_flavor",
                    "yield_measure",
                )
            },
        ),
    )
    form = ProductAdminForm
    readonly_fields = ("yield_measure",)

    def yield_measure(self, obj):
        if obj.category:
            return obj.category.yield_measure
        return ""

    yield_measure.short_description = "Medida de Rendimento"


class ProductDataSheetForm(forms.ModelForm):
    class Meta:
        model = ProductDataSheet
        fields = "__all__"
        widgets = {
            # 'flavors': forms.CheckboxSelectMultiple,
        }

    # def __init__(self, *args, **kwargs):
    #    super().__init__(*args, **kwargs)
    #    # Exibe apenas sabores da mesma categoria do produto selecionado
    #    product = None
    #    if "product" in self.data:
    #        try:
    #            product_id = int(self.data.get("product"))
    #            product = Product.objects.get(pk=product_id)
    #        except (ValueError, TypeError, Product.DoesNotExist):
    #            pass
    #    elif self.instance.pk and self.instance.product:
    #        product = self.instance.product
    #    if product:
    #        self.fields["flavor"].queryset = Flavor.objects.filter(
    #            category=product.category
    #        )
    #    else:
    #        self.fields["flavor"].queryset = Flavor.objects.none()


class ProductDataSheetRecipeInline(admin.TabularInline):
    model = ProductDataSheetRecipe
    extra = 0


@admin.register(ProductDataSheet)
class ProductDataSheetAdmin(admin.ModelAdmin):
    list_display = (
        "product",
        "flavor",
    )
    search_fields = ("product__name",)
    list_filter = ("product", "flavor")
    ordering = (
        "product",
        "flavor",
    )
    fieldsets = ((None, {"fields": ("product", "flavor")}),)
    form = ProductDataSheetForm
    inlines = [ProductDataSheetRecipeInline]


class ProductionItemInline(admin.TabularInline):
    model = ProductionItem
    extra = 1


@admin.register(ProductionBatch)
class ProductionBatchAdmin(admin.ModelAdmin):
    list_display = ("production_date",)
    fieldsets = ((None, {"fields": ("production_date",)}),)
    inlines = [ProductionItemInline]
    actions = ["gerar_relatorio_producao"]

    @admin.action(
        description="Gerar relatório de produção para os registros selecionados"
    )
    def gerar_relatorio_producao(self, request, queryset):

        report_items = []

        for registro in queryset:
            report_item = {
                "title": "Produção de 6 a 10 de Outubro/2025",
                "recipe_resumes": [
                    {
                        "title": "Massas",
                        "items": [
                            {"name": "Baunilha", "quantity": "6350g"},
                            {"name": "Chocolate", "quantity": "2550g"},
                            {"name": "Chocolatudo", "quantity": "3700g"},
                        ],
                        "total": {"quantity": "6350g"},
                    },
                    {
                        "title": "Coberturas",
                        "items": [{"name": "Buttercream", "quantity": "5420g"}],
                        "total": {"quantity": "5420g"},
                    },
                    {
                        "title": "Recheios",
                        "items": [
                            {"name": "Brigadeiro Branco", "quantity": "2850g"},
                            {"name": "Brigadeiro Chocolate", "quantity": "4500g"},
                            {"name": "Geleia de Morango", "quantity": "200g"},
                            {"name": "Geleia de Frutas Vermelhas", "quantity": "250g"},
                        ],
                        "total": {"quantity": "6350g"},
                    },
                ],
            }
            report_items.append(report_item)

        context = {
            "registros_selecionados": queryset.count(),
            "report_items": report_items,
            "generation_date": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
            "company_name": "Dolce Stuppendo",
            "opts": self.model._meta,  # Necessário para o template do admin
            "site_header": self.admin_site.site_header,  # Para manter o layout do admin
            "site_title": self.admin_site.site_title,
            "title": "Relatório de Produção em Lote",  # Título da página do relatório
            "has_permission": True,  # Assume que o usuário tem permissão para a ação
        }

        return TemplateResponse(request, "relatorio_producao_template.html", context)


class RecipeIngredientInline(admin.TabularInline):
    model = RecipeIngredient
    extra = 0


class RecipeStepInline(admin.TabularInline):
    model = RecipeStep
    extra = 0


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "measure_quantity",
        "measure_unit",
        "recipe_category",
    )
    search_fields = (
        "name",
        "description",
    )
    list_filter = ("recipe_category",)
    ordering = ("name",)
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "name",
                    "description",
                    "measure_quantity",
                    "measure_unit",
                    "recipe_category",
                )
            },
        ),
    )
    inlines = [RecipeIngredientInline, RecipeStepInline]


@admin.register(RecipeCategory)
class RecipeCategoryAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "description",
    )
    search_fields = (
        "name",
        "description",
    )
    ordering = ("name",)
    fieldsets = ((None, {"fields": ("name", "description")}),)
