from django import forms
from django.shortcuts import render
import pandas as pd
from .services import loadxls_order_service


class ExcelUploadForm(forms.Form):
    file = forms.FileField(
        widget=forms.FileInput(attrs={"class": "form-control"}),
        label="arquivo de pedidos",
        )


def loadxls_order_view(request):
    if request.method == "POST":
        form = ExcelUploadForm(request.POST, request.FILES)
        if form.is_valid():
            excel_file = request.FILES["file"]
            df = pd.read_excel(excel_file, engine="openpyxl")
            orders = loadxls_order_service(df)
            return render(
                request, "import_orders_xls.html", {"form": form, "orders": orders}
            )

    else:
        form = ExcelUploadForm()
    return render(request, "import_orders_xls.html", {"form": form})
