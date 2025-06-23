# sua_app/views.py (ou onde você está construindo seu relatório)
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from datetime import datetime
from .services import create_report


class ManufatureOrdersAPIView(APIView):
    """Faz uma par de coisa"""

    def get(self, request):

        if not request.query_params.get("begin_date"):
            return Response(
                {"error":
                 "Os parâmetros 'begin_date' e 'end_date' são obrigatórios."
                 },
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not request.query_params.get("end_date"):
            return Response(
                {"error":
                 "Os parâmetros 'begin_date' e 'end_date' são obrigatórios."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            begin_date = datetime.strptime(
                request.query_params.get("begin_date"), "%Y-%m-%d"
            )
        except ValueError:
            return Response(
                {"error": "Formato de data inválido. Use YYYY-MM-DD."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            end_date = datetime.strptime(
                request.query_params.get("end_date"), "%Y-%m-%d"
            )
        except ValueError:
            return Response(
                {"error": "Formato de data inválido. Use YYYY-MM-DD."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        from orders.models import StatusChoices
        content = create_report(
            begin_date=begin_date,
            end_date=end_date,
            status_list=[StatusChoices.EM_PREPARACAO]
            )

        return Response(
            {
                "head": {"begin_date": begin_date, "end_date": end_date},
                "content": content,
            }
        )
