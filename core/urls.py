"""
URL configuration for core project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path, include

from products.views import (
    home_view,
    IngredientAPIView,
    RecipeIngredientAPIView,
    RecipeDetalheAPIView,
    RecipeIngredientDetalheAPIView,
    IngredientDetalheAPIView,
    RecipeAPIView,
    contato_view,
)
from orders.views import loadxls_order_view

# from django.conf.urls.static import static
urlpatterns = [
    path("admin/", admin.site.urls),
    path(
        "api/v1/products/ingredient",
        IngredientAPIView.as_view(),
        name="ingredient-list",
    ),
    path(
        "api/v1/products/ingredient/<int:pk>",
        IngredientDetalheAPIView.as_view(),
        name="ingredient-detail",
    ),
    path(
        "api/v1/products/recipe",
        RecipeAPIView.as_view(),
        name="recipe-list"
    ),
    path(
        "api/v1/products/recipe/<int:pk>",
        RecipeDetalheAPIView.as_view(),
        name="recipe-detail",
    ),
    path(
        "api/v1/products/recipe-ingredient",
        RecipeIngredientAPIView.as_view(),
        name="recipe-ingredient-list",
    ),
    path(
        "api/v1/products/recipe-ingredient/<int:pk>",
        RecipeIngredientDetalheAPIView.as_view(),
        name="recipe-ingredient-detail",
    ),
    path("producao", contato_view, name="linha_producao"),
    path("api/v1/manufature/", include("manufature.urls_api")),
    path("", home_view, name="home"),
    path("orders/upload/", loadxls_order_view, name="loadxls_order_view"),
]


# + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
