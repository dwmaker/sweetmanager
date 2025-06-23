from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from django import forms
from manufature.services import create_report
from .services import show_datasheets
from datetime import date, timedelta
from .serializers import (
    IngredientSerializer,
    RecipeSerializer,
    RecipeIngredientSerializer,
)
from products.models import Ingredient, Recipe, RecipeIngredient
from orders.models import StatusChoices


class IngredientAPIView(APIView):
    """Faz uma par de coisa"""

    def get(self, request) -> Ingredient:
        queryset = Ingredient.objects.all()
        serializer = IngredientSerializer(
            queryset, many=True
        )  # many=True para lista de objetos
        return Response(serializer.data)


class IngredientDetalheAPIView(APIView):
    def get(self, request, pk):
        try:
            instance = Ingredient.objects.get(pk=pk)
            serializer = IngredientSerializer(instance)
            return Response(serializer.data)
        except Ingredient.DoesNotExist:
            return Response({"error": "Objeto não encontrado"}, status=404)


class RecipeAPIView(APIView):
    def get(self, request):
        queryset = Recipe.objects.all()
        serializer = RecipeSerializer(
            queryset, many=True
        )  # many=True para lista de objetos
        return Response(serializer.data)


class RecipeDetalheAPIView(APIView):
    def get(self, request, pk):
        try:
            instance = Recipe.objects.get(pk=pk)
            serializer = RecipeSerializer(instance)
            return Response(serializer.data)
        except Recipe.DoesNotExist:
            return Response({"error": "Objeto não encontrado"}, status=404)


class RecipeIngredientAPIView(APIView):
    def get(self, request):
        queryset = RecipeIngredient.objects.all()
        serializer = RecipeIngredientSerializer(
            queryset, many=True
        )  # many=True para lista de objetos
        return Response(serializer.data)


class RecipeIngredientDetalheAPIView(APIView):
    def get(self, request, pk):
        try:
            instance = RecipeIngredient.objects.get(pk=pk)
            serializer = RecipeIngredientSerializer(instance)
            return Response(serializer.data)
        except RecipeIngredient.DoesNotExist:
            return Response({"error": "Objeto não encontrado"}, status=404)


def calcula_datas(current_date: date):
    my_dict = [
        {"name": "Segunda", "add_begin": 0, "add_end": 8},
        {"name": "Terça",   "add_begin": 0, "add_end": 7},
        {"name": "Quarta",  "add_begin": 0, "add_end": 6},
        {"name": "Quinta",  "add_begin": 0, "add_end": 5},
        {"name": "Sexta",   "add_begin": 0, "add_end": 4},
        {"name": "Sábado",  "add_begin": 0, "add_end": 3},
        {"name": "Domingo", "add_begin": 0, "add_end": 9}
    ]

    row = my_dict[current_date.weekday()]
    begin_date = current_date + timedelta(days=row["add_begin"])
    end_date = current_date + timedelta(days=row["add_end"])
    return begin_date, end_date


class ContatoForm(forms.Form):
    begin_date = forms.DateField(
        initial=calcula_datas(date.today())[0],
        widget=forms.DateInput(attrs={"class": "form-control"}),
        label="Data Inicial",
    )
    end_date = forms.DateField(
        initial=calcula_datas(date.today())[1],
        widget=forms.DateInput(attrs={"class": "form-control"}),
        label="Data Final",
    )


def home_view(request):

    recipes = RecipeSerializer(Recipe.objects.all(), many=True).data
    datasheets = show_datasheets()
    return render(
        request,
        "home.html",
        {
            "recipes": recipes,
            "datasheets": datasheets,
        },
    )


def contato_view(request):
    report = None
    begin_date = None
    end_date = None

    if request.method == "POST":
        form = ContatoForm(request.POST)
        if form.is_valid():
            begin_date = form.cleaned_data["begin_date"]
            end_date = form.cleaned_data["end_date"]
            report = create_report(begin_date=begin_date, end_date=end_date, status_list=[StatusChoices.EM_PREPARACAO])

    else:
        form = ContatoForm()

    return render(
        request,
        "producao.html",
        {
            "form": form,
            "begin_date": begin_date,
            "end_date": end_date,
            "report": report,
        },
    )
