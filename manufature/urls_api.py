from manufature.views import ManufatureOrdersAPIView

from django.urls import path

urlpatterns = [
    path(
        "manufature-orders", ManufatureOrdersAPIView.as_view(), name="manufature-orders"
    )
]
