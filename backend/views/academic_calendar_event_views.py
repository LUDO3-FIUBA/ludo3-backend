from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from backend.models.academic_calendar_event import AcademicCalendarEvent
from backend.serializers.academic_calendar_event_serializer import AcademicCalendarEventSerializer
from backend.views.base_view import BaseViewSet

MOBILE_CATEGORIES = {AcademicCalendarEvent.Category.STUDENT, AcademicCalendarEvent.Category.TEACHER}


class AcademicCalendarEventViewSet(BaseViewSet):
    permission_classes = [IsAuthenticated]
    queryset = AcademicCalendarEvent.objects.all()
    serializer_class = AcademicCalendarEventSerializer

    @swagger_auto_schema(
        tags=["Academic Calendar"],
        operation_summary="Lists academic calendar events visible in the app",
        manual_parameters=[
            openapi.Parameter(
                "year",
                openapi.IN_QUERY,
                description="Filter by academic year (e.g. 2026). Defaults to current year.",
                type=openapi.TYPE_INTEGER,
            ),
        ],
    )
    def list(self, request):
        from datetime import date
        year = request.query_params.get("year", date.today().year)
        qs = self.get_queryset().filter(
            category__in=MOBILE_CATEGORIES,
            year=year,
        )
        return Response(AcademicCalendarEventSerializer(qs, many=True).data, status.HTTP_200_OK)
