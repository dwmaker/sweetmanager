from django.db import models


class BakingPan(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name="Nome da Forma")
    description = models.TextField(blank=True, null=True, verbose_name="Descrição")
    size = models.CharField(
        max_length=50, blank=False, null=False, verbose_name="Tamanho"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Criado em")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Atualizado em")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Forma de Assar"
        verbose_name_plural = "Formas de Assar"
        ordering = ["name"]
        db_table = "eqp_baking_pan"


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name="Nome")
    description = models.TextField(blank=True, null=True, verbose_name="Descrição")

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Criado em")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Atualizado em")

    class Meta:
        verbose_name = "Categoria"
        verbose_name_plural = "Categorias"
        ordering = ["name"]
        db_table = "prd_category"

    def __str__(self):
        return self.name


class Flavor(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name="Nome do Sabor")
    description = models.TextField(blank=True, null=True, verbose_name="Descrição")
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name="flavors",
        verbose_name="Categoria",
    )
    is_active = models.BooleanField(default=True, verbose_name="Ativo")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Criado em")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Atualizado em")

    class Meta:
        verbose_name = "Sabor"
        verbose_name_plural = "Sabores"
        ordering = ["name"]
        db_table = "prd_flavor"

    def __str__(self):
        return f"{self.name} ({self.category})"


class Product(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name="Nome")
    description = models.TextField(blank=True, null=True, verbose_name="Descrição")
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name="products",
        verbose_name="Categoria",
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Criado em")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Atualizado em")
    # yield_quantity = models.IntegerField(
    #    blank=False, null=False, verbose_name="Quantidade de Rendimento"
    # )
    max_flavor_quantity = models.IntegerField(
        blank=False, null=False, default=1, verbose_name="Quantidade Máxima de Sabores"
    )
    min_quantity_per_flavor = models.IntegerField(
        blank=False, null=False, default=1, verbose_name="Quantidade Mínima por Sabor"
    )
    is_active = models.BooleanField(default=True, verbose_name="Ativo")
    flavors = models.ManyToManyField(
        Flavor, related_name="products", blank=True, verbose_name="Sabores"
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Produto"
        verbose_name_plural = "Produtos"
        ordering = ["name"]
        db_table = "prd_product"

class MeasureUnitChoices(models.TextChoices):
    G = 'g', 'g'
    KG = 'kg', 'kg'




class Ingredient(models.Model):
    name = models.CharField(
        max_length=100, unique=True, verbose_name="Nome do Ingrediente"
    )
    description = models.TextField(blank=True, null=True, verbose_name="Descrição")

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Criado em")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Atualizado em")

    class Meta:
        verbose_name = "Ingrediente"
        verbose_name_plural = "Ingredientes"
        ordering = ["name"]
        db_table = "man_ingredient"

    def __str__(self):
        return self.name


class RecipeCategory(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name="Nome")
    description = models.TextField(blank=True, null=True, verbose_name="Descrição")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Criado em")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Atualizado em")

    class Meta:
        verbose_name = "Categoria de Receita"
        verbose_name_plural = "Categorias de Receita"
        ordering = ["name"]
        db_table = "man_recipe_category"

    def __str__(self):
        return self.name


class Recipe(models.Model):
    name = models.CharField(max_length=100, verbose_name="Nome da Receita")
    description = models.TextField(blank=True, null=True, verbose_name="Descrição")
    recipe_category = models.ForeignKey(
        RecipeCategory,
        on_delete=models.PROTECT,
        default=1,
        related_name="recipes",
        verbose_name="Categoria de Receita",
    )
    measure_unit = models.CharField(max_length=10, choices=MeasureUnitChoices.choices, null=False, blank=False, default=MeasureUnitChoices.G, verbose_name="Medida de Rendimento",)
    measure_quantity = models.FloatField(
        blank=False, null=False, verbose_name="Quantidade de Rendimento"
    )

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Criado em")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Atualizado em")

    class Meta:
        verbose_name = "Receita"
        verbose_name_plural = "Receitas"
        db_table = "man_recipe"
        ordering = ["name"]

    def __str__(self):
        return f"{self.name}"


class RecipeIngredient(models.Model):

    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name="recipe_ingredients",
        verbose_name="Receita",
    )

    position = models.PositiveIntegerField(default=0, verbose_name="Posição na Receita")

    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name="ingredient_recipes",
        verbose_name="Ingrediente",
    )

    measure_quantity = models.FloatField(
        verbose_name="Quantidade", blank=False, null=False
    )
    measure_unit = models.CharField(max_length=10, choices=MeasureUnitChoices.choices, null=False, blank=False, default=MeasureUnitChoices.G, verbose_name="Medida de Rendimento",)

    class Meta:
        verbose_name = "Ingrediente da Receita"
        verbose_name_plural = "Ingredientes da Receita"
        unique_together = ("recipe", "ingredient")
        db_table = "man_recipe_ingredient"
        ordering = ["recipe", "position"]

    def __str__(self):
        return (
            f"{self.ingredient.name} - {self.measure_quantity} {self.measure_unit}"
        )


class ProductDataSheet(models.Model):

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="data_sheets",
        verbose_name="Produto",
    )
    flavor = models.ForeignKey(
        Flavor,
        on_delete=models.CASCADE,
        related_name="data_sheets",
        verbose_name="Sabor",
    )

    description = models.TextField(
        blank=True, null=True, verbose_name="Descrição da Ficha Técnica"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Criado em")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Atualizado em")

    class Meta:
        verbose_name = "Ficha Técnica"
        verbose_name_plural = "Fichas Técnicas"
        unique_together = ("product", "flavor")
        ordering = ["product", "flavor"]
        db_table = "man_product_data_sheet"

    def __str__(self):
        return f"Ficha Técnica: {self.product.name} - {self.flavor.name}"


class ProductDataSheetRecipe(models.Model):
    multiple = models.FloatField(verbose_name="Multiplicador", default=1)
    data_sheet = models.ForeignKey(
        ProductDataSheet,
        on_delete=models.CASCADE,
        related_name="recipes",
        verbose_name="Ficha Técnica",
    )
    baking_pan = models.ForeignKey(
        BakingPan,
        on_delete=models.PROTECT,
        related_name="data_sheets",
        verbose_name="Forma de Assar",
        null=True,
        blank=True,
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name="data_sheet_recipes",
        verbose_name="Receita",
    )

    measure_quantity = models.FloatField(
        blank=False, null=False, verbose_name="Quantidade de Rendimento"
    )
    measure_unit = models.CharField(max_length=10, choices=MeasureUnitChoices.choices, null=False, blank=False, default=MeasureUnitChoices.G, verbose_name="Medida de Rendimento",)

    class Meta:
        db_table = "man_product_data_sheet_recipe"
        verbose_name = "Receita da Ficha Técnica"
        verbose_name_plural = "Receitas da Ficha Técnica"

    def __str__(self):
        return f"Receita: {self.recipe.name} - Ficha Técnica: {self.data_sheet.product.name} - {self.data_sheet.flavor.name}"


class ProductionBatch(models.Model):
    production_date = models.DateField(
        auto_now_add=False, verbose_name="Data de Produção"
    )

    def __str__(self):
        return f"Lote de Produção: {self.production_date}"

    class Meta:
        db_table = "man_production_batch"
        verbose_name = "Lote de Produção"
        verbose_name_plural = "Lotes de Produção"
        ordering = ["production_date"]


class ProductionItem(models.Model):
    production_batch = models.ForeignKey(
        ProductionBatch,
        on_delete=models.CASCADE,
        related_name="items",
        verbose_name="Lote de Produção",
    )

    product_data_sheet = models.ForeignKey(
        ProductDataSheet,
        on_delete=models.CASCADE,
        related_name="production_items",
        verbose_name="Ficha Técnica",
    )
    quantity = models.IntegerField(
        verbose_name="Quantidade Produzida", blank=False, null=False
    )

    class Meta:
        db_table = "man_production_item"
        verbose_name = "Ítem de Produção"
        verbose_name_plural = "Items de Produção"
        ordering = ["production_batch", "product_data_sheet"]

    def __str__(self):
        return f"Lote: {self.product_data_sheet} - {self.quantity} unidades"


from django.db import models


class RecipeStep(models.Model):
    num = models.PositiveIntegerField(default=1)
    description = models.CharField(blank=True, null=True, verbose_name="Descrição")
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        default=1,
        null=False,
        blank=False,
        related_name="recipes",
        verbose_name="Passos de Receita",
    )

    class Meta:
        verbose_name = "Passo de Receita"
        verbose_name_plural = "Passos de Receita"
        ordering = ["recipe", "num"]
