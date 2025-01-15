from rest_framework import filters
from django_filters.rest_framework import DjangoFilterBackend
from django.utils.timezone import now
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.views import APIView
from hrms_app.hrms.serializers import *
from rest_framework import status
from django.utils.translation import gettext_lazy as _
from rest_framework.generics import (
    RetrieveAPIView,
    ListAPIView,
    UpdateAPIView,
    CreateAPIView,
    DestroyAPIView,
)
from rest_framework.exceptions import ValidationError

from rest_framework import viewsets
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from hrms_app.hrms.utils import *
from rest_framework import viewsets
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404
from django.core.exceptions import ValidationError
from django.db.models import Q


###########################################################################
########   User Attendance Log modules
########   By Divyanshu
###########################################################################


class AttendanceSettingViewSet(viewsets.ModelViewSet):

    queryset = AttendanceSetting.objects.all()
    serializer_class = AttendanceSettingSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            self.perform_create(serializer)
            # Custom response
            return create_response(
                status="error",
                message=_("Attendance Setting created successfully"),
                data=serializer.data,
                status_code=status.HTTP_201_CREATED,
            )
        return create_response(
            status="error",
            message=_("Error creating Attendance Setting"),
            data=serializer.errors,
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return create_response(
            status="success",
            message=_("Attendance Settings fetched successfully"),
            data=serializer.data,
            status_code=status.HTTP_200_OK,
        )

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return create_response(
            status="success",
            message=_("Attendance Setting details"),
            data=serializer.data,
            status_code=status.HTTP_200_OK,
        )


class AttendanceStatusColorViewSet(viewsets.ModelViewSet):
    queryset = AttendanceStatusColor.objects.all()
    serializer_class = AttendanceStatusColorSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            self.perform_create(serializer)
            # Custom response
            return create_response(
                status="error",
                message=_("Attendance Status Color created successfully"),
                data=serializer.data,
                status_code=status.HTTP_201_CREATED,
            )
        return create_response(
            status="error",
            message=_("Error creating Attendance Status Color"),
            data=serializer.errors,
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    # Override the list method
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return create_response(
            status="success",
            message=_("Attendance Status Colors fetched successfully"),
            data=serializer.data,
            status_code=status.HTTP_200_OK,
        )

    # Override the retrieve method
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return create_response(
            status="success",
            message=_("Attendance Status Color details"),
            data=serializer.data,
            status_code=status.HTTP_200_OK,
        )


class AttendanceLogViewSet(viewsets.ModelViewSet):
    queryset = AttendanceLog.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = AttendanceLogSerializer
    filter_backends = [
        DjangoFilterBackend,
        filters.OrderingFilter,
        filters.SearchFilter,
    ]
    ordering_fields = ["start_date", "end_date", "created_at"]
    search_fields = ["title", "reason"]
    lookup_field = "pk"

    def get_queryset(self):
        user = self.request.user
        queryset = AttendanceLog.objects.filter(applied_by=user)

        # Get the current month and year
        current_month = now().month
        current_year = now().year

        # Handle from_date query param
        from_date = self.request.query_params.get("from_date")
        if from_date:
            try:
                parsed_date = datetime.strptime(from_date, "%Y-%m-%d %H:%M:%S.%f")
                month = parsed_date.month
                year = parsed_date.year
            except ValueError:
                month = current_month
                year = current_year
        else:
            month = current_month
            year = current_year

        queryset = queryset.filter(start_date__year=year, start_date__month=month)

        from_param = self.request.query_params.get("from", None)
        to_param = self.request.query_params.get("to", None)
        if from_param and to_param:
            queryset = queryset.filter(
                start_date__gte=from_param, end_date__lte=to_param
            )

        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return create_response(
            status="success",
            message=_("Attendance logs retrieved successfully."),
            data=serializer.data,
            status_code=status.HTTP_200_OK,
        )

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        return create_response(
            status="success",
            message=_("Attendance log created successfully."),
            data=response.data,
            status_code=status.HTTP_201_CREATED,
        )
        
    def update(self, request, *args, **kwargs):
        try:
            log = get_object_or_404(AttendanceLog,id=self.request.data.get('id'))
            serializer = self.get_serializer(log, data=self.request.data)
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)
            return create_response(
                status="success",
                message=_("Attendance Log updated successfully."),
                data=serializer.data,
                status_code=status.HTTP_200_OK,
            )
        except Exception as e:
            print(e)
            return create_response(
                status="error",
                message=_("Failed to update attendance log."),
                data=e.detail,
                status_code=status.HTTP_400_BAD_REQUEST,
            )

    def partial_update(self, request, pk=None, *args, **kwargs):
        kwargs["partial"] = True
        return self.update(request, pk=None, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        attendance_log = get_object_or_404(AttendanceLog, id=kwargs.get('pk'))
        serializer = self.get_serializer(attendance_log)
        return create_response(
            status="success",
            message=_("Attendance log retrieved successfully."),
            data=serializer.data,
            status_code=status.HTTP_200_OK,
        )

    def destroy(self, request, *args, **kwargs):
        super().destroy(request, *args, **kwargs)
        return create_response(
            status="success",
            message=_("Attendance log deleted successfully."),
            status_code=status.HTTP_204_NO_CONTENT,
        )

    @action(detail=True, methods=["post"])
    def approve(self, request, pk=None):
        attendance_log = self.get_object()
        reason = request.data.get("reason", None)
        attendance_log.approve(action_by=request.user, reason=reason)
        return Response({"status": "approved"}, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"])
    def reject(self, request, pk=None):
        attendance_log = self.get_object()
        reason = request.data.get("reason", None)
        attendance_log.reject(action_by=request.user, reason=reason)
        return Response({"status": "rejected"}, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"])
    def recommend(self, request, pk=None):
        attendance_log = self.get_object()
        reason = request.data.get("reason", None)
        attendance_log.recommend(action_by=request.user, reason=reason)
        return Response({"status": "recommended"}, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"])
    def notrecommend(self, request, pk=None):
        attendance_log = self.get_object()
        reason = request.data.get("reason", None)
        attendance_log.notrecommend(action_by=request.user, reason=reason)
        return Response({"status": "not recommended"}, status=status.HTTP_200_OK)


#################  End Attendance Logs Modules  ############################


class UserViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer
    lookup_field = "id"


class CustomUserDetailAPIView(RetrieveAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer


class CurrentUserAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        serializer = CustomUserSerializer(user)
        return Response(serializer.data)


class PersonalDetailsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            personal_details = PersonalDetails.objects.get(user=request.user)
            serializer = PersonalDetailsSerializer(personal_details)
            return create_response(
                status="success",
                message="Personal details fetched successfully.",
                data=serializer.data,
            )
        except PersonalDetails.DoesNotExist:
            return create_response(
                status="error",
                message="Personal details not found.",
                data=None,
                status_code=404,
            )
        except Exception as e:
            return create_response(
                status="error",
                message=f"An error occurred: {str(e)}",
                data=None,
                status_code=500,
            )


class EmployeeShiftView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            # Fetch shifts for the authenticated user
            shifts = EmployeeShift.objects.filter(employee=request.user)
            serializer = EmployeeShiftSerializer(shifts, many=True)
            response_data = {
                "status": "success",
                "message": _("Employee shifts fetched successfully."),
                "data": serializer.data,
            }
            return Response(response_data, status=status.HTTP_200_OK)
        except Exception as e:
            response_data = {
                "status": "error",
                "message": f"An error occurred: {str(e)}",
                "data": None,
            }
            return Response(response_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class AttendanceChoicesView(APIView):

    def get(self, request):
        choices = {
            "attendance_regularity_status": [
                {"key": key, "value": value}
                for key, value in settings.ATTENDANCE_REGULARISED_STATUS_CHOICES
            ],
            "attendance_status": [
                {"key": key, "value": value}
                for key, value in settings.ATTENDANCE_STATUS_CHOICES
            ],
            "attendance_log_status": [
                {"key": key, "value": value}
                for key, value in settings.ATTENDANCE_LOG_STATUS_CHOICES
            ],
            "tour_status": [
                {"key": key, "value": value}
                for key, value in settings.TOUR_STATUS_CHOICES
            ],
            "approval_type": [
                {"key": key, "value": value}
                for key, value in settings.APPROVAL_TYPE_CHOICES
            ],
            "leave_status": [
                {"key": key, "value": value}
                for key, value in settings.LEAVE_STATUS_CHOICES
            ],
            "start_leave_type": [
                {"key": key, "value": value}
                for key, value in settings.START_LEAVE_TYPE_CHOICES
            ],
        }
        return create_response(
            status="success",
            message="Success",
            data=choices,
            status_code=status.HTTP_200_OK,
        )


class LeaveApplicationViewSet(viewsets.ModelViewSet):
    """
    A viewset for viewing and editing leave application instances.
    """

    queryset = LeaveApplication.objects.all()
    serializer_class = LeaveApplicationSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'id'

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            return create_response(
                status="success",
                message=_("Leave sent to manager. Wait for approval"),
                data=serializer.data,
                status_code=status.HTTP_201_CREATED,
            )
        except serializers.ValidationError as e:
            return create_response(
                status="error",
                message=_("There was an error with your leave application."),
                data={"non_field_errors": e.detail.get("non_field_errors", [])},
                status_code=status.HTTP_400_BAD_REQUEST,
            )

    def update(self, request, *args, **kwargs):
        """Update the leave application with special handling for status updates."""
        leave_application = self.get_object()
        serializer = self.get_serializer(
            leave_application, data=request.data, partial=True
        )
        try:
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)

            action_by = request.user
            if leave_application.status in [
                settings.APPROVED,
                settings.REJECTED,
                settings.CANCELLED,
            ]:
                LeaveLog.create_log(
                    leave_application, action_by, leave_application.status
                )
            else:
                LeaveLog.create_log(leave_application, action_by, "Updated")

            return create_response(
                status="success",
                message=_("Leave application updated successfully."),
                data=serializer.data,
                status_code=status.HTTP_200_OK,
            )
        except serializers.ValidationError as e:
            return create_response(
                status="error",
                message=_("There was an error updating your leave application."),
                data={"non_field_errors": e.detail.get("non_field_errors", [])},
                status_code=status.HTTP_400_BAD_REQUEST,
            )

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()  # Get the LeaveApplication instance
        serializer = self.get_serializer(instance)
        return create_response(
            status="success",
            message=_("Success"),
            data=serializer.data,
            status_code=status.HTTP_200_OK,
        )

    def destroy(self, request, *args, **kwargs):
        leave_application = self.get_object()
        leave_application.delete()
        return create_response(
            status="success",
            message=_("Leave application deleted successfully"),
            data=None,
            status_code=status.HTTP_200_OK,
        )

    def list(self, request, *args, **kwargs):
        leave_applications = self.filter_queryset(self.get_queryset())

        return self._paginate_results(leave_applications, request)

    def _paginate_results(self, queryset, request):
        """Helper method to paginate and serialize the results."""
        paginator = PageNumberPagination()
        paginated_queryset = paginator.paginate_queryset(queryset, request)
        request_type = self.request.query_params.get("type", "")
        is_manager = request_type == "requested"
        serializer = LeaveApplicationSerializer(
            paginated_queryset,
            many=True,
            context={"request": request, "isManager": is_manager},
        )
        return paginator.get_paginated_response(serializer.data)

    def get_queryset(self):
        """Restricts the returned leave applications based on the user type."""
        user = self.request.user
        queryset = LeaveApplication.objects.none()  # Default to an empty queryset

        # Determine the type of request
        request_type = self.request.query_params.get("type")

        # Set the isManager flag based on the request type
        self.request.is_manager = request_type == "requested"

        if request_type == "requested" and hasattr(user, "employees") and user.employees.exists():
            queryset = LeaveApplication.objects.filter(appliedBy__in=user.employees.all())
        elif request_type == "own":
            queryset = LeaveApplication.objects.filter(appliedBy=user)

        # If no valid request_type is specified, return an empty queryset
        if queryset is None:
            return LeaveApplication.objects.none()

        from_date = self.request.query_params.get("from_date")
        to_date = self.request.query_params.get("to_date")
        status_filter = self.request.query_params.get("status")

        if from_date:
            try:
                from_date = timezone.datetime.strptime(from_date, "%Y-%m-%d").date()
                queryset = queryset.filter(startDate__gte=from_date)
            except ValueError:
                raise ValueError("Invalid date format for from_date. Use YYYY-MM-DD.")

        if to_date:
            try:
                to_date = timezone.datetime.strptime(to_date, "%Y-%m-%d").date()
                queryset = queryset.filter(endDate__lte=to_date)
            except ValueError:
                raise ValueError("Invalid date format for to_date. Use YYYY-MM-DD.")

        if status_filter:
            queryset = queryset.filter(status=status_filter)

        return queryset.distinct()

class UserLeaveOpeningsViewSet(viewsets.ModelViewSet):
    """
    A viewset for managing user-specific Leave Balance Openings.
    """

    permission_classes = [IsAuthenticated]
    serializer_class = LeaveBalanceOpeningSerializer

    def get_queryset(self):
        user = self.request.user
        year = self.request.query_params.get("year", timezone.now().year)
        return LeaveBalanceOpenings.objects.filter(user=user, year=year)

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return create_response(
            status="success",
            message=_("Leave openings retrieved successfully."),
            data=serializer.data,
            status_code=status.HTTP_200_OK,
        )

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return create_response(
            status="success",
            message=_("Leave opening retrieved successfully."),
            data=serializer.data,
            status_code=status.HTTP_200_OK,
        )

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return create_response(
            status="success",
            message=_("Leave opening created successfully."),
            data=serializer.data,
            status_code=status.HTTP_201_CREATED,
        )

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        create_response(
            status="success",
            message=_("Leave opening updated successfully."),
            data=serializer.data,
            status_code=status.HTTP_200_OK,
        )

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        create_response(
            status="success",
            message=_("Leave opening deleted successfully."),
            status_code=status.HTTP_204_NO_CONTENT,
        )


class LeaveTypeViewSet(viewsets.ModelViewSet):
    queryset = LeaveType.objects.all()
    serializer_class = LeaveTypeSerializer
    permission_classes = [AllowAny]  # Set your permission classes

    def list(self, request, *args, **kwargs):
        # You can override the list method if you want custom behavior
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(
            {
                "status": "success",
                "message": _("Success"),
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )


from rest_framework.decorators import action

from rest_framework.pagination import PageNumberPagination

class HolidaysPagination(PageNumberPagination):
    page_size = 20  # Set the default page size to 20

class HolidayViewSet(viewsets.ModelViewSet):
    queryset = Holiday.objects.all()
    serializer_class = HolidaySerializer
    permission_classes = [AllowAny]
    filter_backends = [filters.OrderingFilter]  # Add other filter backends if needed
    ordering_fields = ["start_date", "end_date"]  # Fields that can be used for ordering
    pagination_class = HolidaysPagination

    def get_queryset(self):
        """
        Optionally restricts the returned holidays to a given date range
        by filtering against `start_date` and `end_date` query parameters.
        """
        queryset = super().get_queryset()
        start_date_str = self.request.query_params.get("start_date", None)
        end_date_str = self.request.query_params.get("end_date", None)

        # Parse the date strings and handle any errors
        try:
            start_date = self._validate_date_format(start_date_str)
            end_date = self._validate_date_format(end_date_str)
        except ValidationError as e:
            raise ValidationError({"error": str(e)})

        # Apply filtering based on valid dates
        if start_date and end_date:
            queryset = queryset.filter(
                start_date__gte=start_date, end_date__lte=end_date
            )
        elif start_date:
            queryset = queryset.filter(start_date__gte=start_date)
        elif end_date:
            queryset = queryset.filter(end_date__lte=end_date)

        return queryset

    def _validate_date_format(self, date_str):
        """
        Validates the format of the given date string.
        Raises a ValidationError if the format is invalid.
        """
        if not date_str:
            return None  # Return None if no date is provided
        try:
            # Try to parse the date using `datetime.strptime` for stricter validation
            return datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            raise ValidationError(
                f"Invalid date format for '{date_str}'. Expected format is 'YYYY-MM-DD'."
            )

    def create(self, request, *args, **kwargs):
        """
        Handle creation of a new Holiday record.
        Returns a custom response with holiday details and message.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)

        return Response(
            {
                "status": "success",
                "message": "Holiday created successfully!",
                "data": serializer.data,
            },
            status=status.HTTP_201_CREATED,
            headers=headers,
        )

    def update(self, request, *args, **kwargs):
        """
        Handle updating a holiday record.
        Returns a custom response with updated holiday details.
        """
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(
            {
                "status": "success",
                "message": "Holiday updated successfully!",
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )

    def list(self, request, *args, **kwargs):
        """
        Handle listing all holiday records.
        Returns a custom response with the list of holidays.
        """
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(
                {
                    "status": "success",
                    "message": "Holiday list retrieved successfully!",
                    "data": serializer.data,
                }
            )

        serializer = self.get_serializer(queryset, many=True)
        return Response(
            {
                "status": "success",
                "message": "Holiday list retrieved successfully!",
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )

    def retrieve(self, request, *args, **kwargs):
        """
        Handle retrieving a single holiday record.
        Returns a custom response with the holiday details.
        """
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(
            {
                "status": "success",
                "message": "Holiday retrieved successfully!",
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )

    def destroy(self, request, *args, **kwargs):
        """
        Handle deleting a holiday record.
        Returns a custom response confirming deletion.
        """
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(
            {"status": "success", "message": "Holiday deleted successfully!"},
            status=status.HTTP_204_NO_CONTENT,
        )

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user, updated_by=self.request.user)

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)


###########################################################################
########   User Notification modules
########   By Divyanshu
###########################################################################
from django.db.models import Q
from django.utils.dateparse import parse_datetime

class UserMonthlyNotificationsListView(ListAPIView):
    """
    API view to fetch notifications for the authenticated user within a date range,
    optionally filtered and paginated.
    """
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = PageNumberPagination  # Enables pagination

    def get_queryset(self):
        """
        Get notifications for the authenticated user.
        """
        user = self.request.user
        return Notification.objects.filter(
            Q(receiver=user) | Q(sender=user)
        ).order_by("-timestamp")

    def list(self, request, *args, **kwargs):
        """
        Override the list method to allow filtering and provide paginated data,
        including the unread notification count.
        """
        queryset = self.get_queryset()

        # Extract date range parameters from the query params
        start_date = request.query_params.get("start_date")
        end_date = request.query_params.get("end_date")

        # Apply filtering based on start_date and end_date if provided
        if start_date:
            start_date_parsed = parse_datetime(start_date)
            if start_date_parsed:
                queryset = queryset.filter(timestamp__gte=start_date_parsed)

        if end_date:
            end_date_parsed = parse_datetime(end_date)
            if end_date_parsed:
                queryset = queryset.filter(timestamp__lte=end_date_parsed)

        # Calculate unread notification count
        unread_count = queryset.filter(is_read=False).count()

        # Paginate the queryset
        page = self.paginate_queryset(queryset)
        if page is not None:
            serialized_data = self.get_serializer(page, many=True).data
            return self.get_paginated_response(
                {
                    "status": "success",
                    "message": "Notifications fetched successfully.",
                    "unread_count": unread_count,  # Add unread notification count
                    "data": serialized_data,
                }
            )

        # If pagination is not applied, serialize and return the entire data
        serialized_data = self.get_serializer(queryset, many=True).data
        return Response(
            {
                "status": "success",
                "message": "Notifications fetched successfully.",
                "unread_count": unread_count,  # Add unread notification count
                "data": serialized_data,
            },
            status=status.HTTP_200_OK,
        )

class UpdateNotificationStatusView(UpdateAPIView):
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = "id"
    def update(self, request, *args, **kwargs):
        try:
            # Get the notification object based on the provided ID
            notification = self.get_object()

            # Mark the notification as read
            notification.is_read = True
            notification.save()

            # Serialize and return the updated notification data
            serializer = self.get_serializer(notification)
            response_data = serializer.data

            # Return the custom centralized response
            return create_response(
                status="success",
                message="Notification marked as read successfully.",
                data=response_data,
                status_code=status.HTTP_200_OK,
            )

        except Notification.DoesNotExist:
            return create_response(
                status="error",
                message="Notification not found.",
                data=None,
                status_code=status.HTTP_404_NOT_FOUND,
            )

        except ValidationError as ve:
            return create_response(
                status="error",
                message="Validation error occurred.",
                data=ve.detail,
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        except Exception as e:
            return create_response(
                status="error",
                message=f"An unexpected error occurred: {str(e)}",
                data=None,
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


##############  Notification Ends  ######################################


###########################################################################
########   User Tour modules
########   By Divyanshu
###########################################################################


class UserTourViewSet(viewsets.ModelViewSet):
    serializer_class = UserTourSerializer
    permission_classes = [AllowAny]
    lookup_field = "id"

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            return create_response(
                status="success",
                message=_("User tour created successfully."),
                data=serializer.data,
                status_code=status.HTTP_201_CREATED,
            )
        except ValidationError as e:
            return create_response(
                status="error",
                message=_("Failed to create user tour."),
                data=e.detail,
                status_code=status.HTTP_400_BAD_REQUEST,
            )

    def retrieve(self, request, id=None, *args, **kwargs):
        try:
            tour = UserTour.objects.get(id=id)
            serializer = self.get_serializer(tour)
            return create_response(
                status="success",
                message=_("User tour retrieved successfully."),
                data=serializer.data,
                status_code=status.HTTP_200_OK,
            )
        except Exception as e:
            return create_response(
                status="error",
                message=_("User tour not found."),
                data=str(e),
                status_code=status.HTTP_404_NOT_FOUND,
            )

    def update(self, request, id=None, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        try:
            tour = UserTour.objects.get(id=id)
            serializer = self.get_serializer(tour, data=request.data, partial=partial)
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)
            return create_response(
                status="success",
                message=_("User tour updated successfully."),
                data=serializer.data,
                status_code=status.HTTP_200_OK,
            )
        except ValidationError as e:
            return create_response(
                status="error",
                message=_("Failed to update user tour."),
                data=e.detail,
                status_code=status.HTTP_400_BAD_REQUEST,
            )

    def partial_update(self, request, id=None, *args, **kwargs):
        kwargs["partial"] = True
        return self.update(request, id, *args, **kwargs)

    def destroy(self, request, id=None, *args, **kwargs):
        try:
            tour = UserTour.objects.get(id=id)
            self.perform_destroy(tour)
            return create_response(
                status="success",
                message=_("User tour deleted successfully."),
                status_code=status.HTTP_204_NO_CONTENT,
            )
        except Exception as e:
            return create_response(
                status="error",
                message=_("Failed to delete user tour."),
                data=str(e),
                status_code=status.HTTP_400_BAD_REQUEST,
            )

    def get_queryset(self):
        user = self.request.user
        queryset = UserTour.objects.all()
        request_type = self.request.query_params.get("type")
        if (
            request_type == "requested"
            and hasattr(user, "employees")
            and user.employees.exists()
        ):
            queryset = queryset.filter(applied_by__in=user.employees.all())
        elif request_type == "own":
            queryset = queryset.filter(applied_by=user)
        else:
            queryset= UserTour.objects.none()

        from_date = self.request.query_params.get("from_date")
        to_date = self.request.query_params.get("to_date")
        tour_status = self.request.query_params.get("status")
        if from_date:
            from_date = datetime.strptime(from_date, "%Y-%m-%d").date()
            queryset = queryset.filter(start_date__gte=from_date)
        if to_date:
            to_date = datetime.strptime(to_date, "%Y-%m-%d").date()
            queryset = queryset.filter(end_date__lte=to_date)

        # Apply status filtering if provided
        if tour_status:
            queryset = queryset.filter(status=tour_status)

        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        request_type = self.request.query_params.get("type", "")
        is_manager = request_type == "requested"
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(
                page, many=True, context={"request": request, "isManager": is_manager}
            )
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return create_response(
            status="success",
            message=_("User tours retrieved successfully."),
            data=serializer.data,
            status_code=status.HTTP_200_OK,
        )

    @action(detail=True, methods=["post"])
    def approved(self, request, id=None):
        tour = get_object_or_404(UserTour, id=id)
        action_by = request.user
        tour.approve(action_by)

        serializer = self.get_serializer(
            tour, context={"request": request, "isManager": True}
        )
        return create_response(
            status="success",
            message=_("Tour approved."),
            data=serializer.data,
            status_code=status.HTTP_200_OK,
        )

    @action(detail=True, methods=["post"])
    def rejected(self, request, id=None):
        tour = get_object_or_404(UserTour, id=id)
        action_by = self.request.user
        reason = request.data.get("reason", None)
        tour.reject(action_by, reason)

        serializer = self.get_serializer(
            tour, context={"request": request, "isManager": True}
        )
        return create_response(
            status="success",
            message=_("Tour rejected."),
            data=serializer.data,
            status_code=status.HTTP_200_OK,
        )

    @action(detail=True, methods=["post"])
    def cancelled(self, request, id=None):
        tour = get_object_or_404(UserTour, id=id)
        action_by = self.request.user
        reason = request.data.get("reason", None)
        tour.cancel(action_by, reason)

        serializer = self.get_serializer(
            tour, context={"request": request, "isManager": True}
        )
        return create_response(
            status="success",
            message=_("Tour cancelled."),
            data=serializer.data,
            status_code=status.HTTP_200_OK,
        )

    @action(detail=True, methods=["post"])
    def pending_cancellation(self, request, id=None):
        tour = get_object_or_404(UserTour, id=id)
        action_by = self.request.user
        reason = request.data.get("reason", None)
        tour.pending_cancel(action_by, reason)

        serializer = self.get_serializer(
            tour, context={"request": request, "isManager": False}
        )
        return create_response(
            status="success",
            message=_("Tour cancellation is pending."),
            data=serializer.data,
            status_code=status.HTTP_200_OK,
        )

    @action(detail=True, methods=["post"])
    def completed(self, request, id=None):
        tour = get_object_or_404(UserTour, id=id)
        action_by = self.request.user
        reason = request.data.get("reason", None)
        tour.complete(action_by, reason)

        serializer = self.get_serializer(
            tour, context={"request": request, "isManager": False}
        )
        return create_response(
            status="success",
            message=_("Tour completed."),
            data=serializer.data,
            status_code=status.HTTP_200_OK,
        )

    @action(detail=True, methods=["post"])
    def extended(self, request, id=None):
        tour = get_object_or_404(UserTour, id=id)
        action_by = self.request.user
        new_end_date = request.data.get("new_end_date")
        new_end_time = request.data.get("new_end_time")
        reason = request.data.get("reason", None)

        if not new_end_date or not new_end_time:
            return create_response(
                status="error",
                message=_("New end date and time are required."),
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        tour.extend(action_by, new_end_date, new_end_time, reason)

        serializer = self.get_serializer(
            tour, context={"request": request, "isManager": False}
        )
        return create_response(
            status="success",
            message=_("Tour extended successfully."),
            data=serializer.data,
            status_code=status.HTTP_200_OK,
        )


##############  Tour Module Ends  ######################################


###########################################################################
########   Device Information modules
########   By Divyanshu
###########################################################################


class DeviceInformationViewSet(viewsets.ModelViewSet):
    serializer_class = DeviceInformationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = DeviceInformation.objects.all()

        device_location = self.request.query_params.get("status", None)

        if device_location:
            queryset = queryset.filter(device_location__id=device_location)
        return queryset

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            return create_response(
                status="success",
                message=_("Device information created successfully."),
                data=serializer.data,
                status_code=status.HTTP_201_CREATED,
            )
        except IntegrityError:
            return create_response(
                status="error",
                message=_("Device with this serial number already exists."),
                data=None,
                status_code=status.HTTP_400_BAD_REQUEST,
            )
        except ValidationError as e:
            return create_response(
                status="error",
                message=_("Validation error."),
                data=e.detail,
                status_code=status.HTTP_400_BAD_REQUEST,
            )

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return create_response(
            status="success",
            message=_("Device information retrieved successfully."),
            data=serializer.data,
            status_code=status.HTTP_200_OK,
        )

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        try:
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)
            return create_response(
                status="success",
                message=_("Device information updated successfully."),
                data=serializer.data,
                status_code=status.HTTP_200_OK,
            )
        except ValidationError as e:
            return create_response(
                status="error",
                message=_("Validation error."),
                data=e.detail,
                status_code=status.HTTP_400_BAD_REQUEST,
            )

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.delete()
        return create_response(
            status="success",
            message=_("Device information deleted successfully."),
            data=None,
            status_code=status.HTTP_204_NO_CONTENT,
        )

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return create_response(
            status="success",
            message=_("Device information retrieved successfully."),
            data=serializer.data,
            status_code=status.HTTP_200_OK,
        )


from django.core.management import call_command
from rest_framework.views import APIView

class ExecutePopulateAttendanceView(APIView):
    """
    API endpoint to manually execute the `populate_attendance` command.
    """

    def post(self, request, *args, **kwargs):
        # Parse input data
        userid = request.data.get("username")
        from_date = request.data.get("from_date")
        to_date = request.data.get("to_date")
        username = None
        if userid:
            user = get_object_or_404(get_user_model(),pk=userid)
            username = user.username
        
        try:
            call_command("pop_att", "--username", username, "--from-date", from_date, "--to-date", to_date)
            return Response({"message": "Data synced successfully!"}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {"error": f"Failed to sync data: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

class Top5EmployeesDurationAPIView(APIView):
    """
    API for aggregating attendance log data, providing top 5 employees based on
    the highest total duration of attendance.
    """

    def filter_queryset(self, queryset):
        """
        Filter data based on `applied_by`, `year`, and `month` query parameters.
        """
        applied_by = self.request.query_params.get('applied_by')
        year = self.request.query_params.get('year')
        month = self.request.query_params.get('month')

        # Validate `year` and `month` parameters
        if not year:
            raise ValidationError({"error": "The 'year' parameter is required."})
        
        try:
            year = int(year)
            if year < 1900 or year > timezone.now().year + 1:
                logging.error(f"Invalid 'year'. Year must be between 1900 and the current year.")
                
                raise ValidationError({"error": "Invalid 'year'. Year must be between 1900 and the current year."})
        except ValueError:
            raise ValidationError({"error": "The 'year' parameter must be a valid integer."})

        if month:
            try:
                month = int(month)
                if month < 1 or month > 12:
                    raise ValidationError({"error": "The 'month' parameter must be between 1 and 12."})
            except ValueError:
                raise ValidationError({"error": "The 'month' parameter must be a valid integer."})

        # Apply filters to the queryset
        if applied_by:
            queryset = queryset.filter(applied_by__username=applied_by)
        
        queryset = queryset.filter(start_date__year=year)
        if month:
            queryset = queryset.filter(start_date__month=month)

        return queryset

    def calculate_working_duration(self, year, month=None):
        """
        Calculate the total working duration for the month/year, excluding Sundays and holidays.
        """
        try:
            # Define the period
            today = timezone.now().date()
            if month:
                first_day = timezone.datetime(year, month, 1).date()
                last_day = today if today.year == year and today.month == month else first_day.replace(month=month + 1) - timedelta(days=1)
            else:
                first_day = timezone.datetime(year, 1, 1).date()
                last_day = timezone.datetime(year, 12, 31).date()

            # Get holidays
            holidays = Holiday.objects.filter(start_date__range=[first_day, last_day])
            
            # Calculate working days
            working_days = [
                day for day in (first_day + timedelta(n) for n in range((last_day - first_day).days + 1))
                if day.weekday() != 6 and not holidays.filter(start_date=day).exists()
            ]
            return (len(working_days) * 8)-8

        except Exception as e:
            logging.error(f"{str(e)}")
            raise ValidationError({"error": f"Failed to calculate working duration: {str(e)}"})

    def get(self, request, *args, **kwargs):
        """
        Handle GET requests to provide top 5 employees with the highest total duration
        and total working duration for the specified month/year.
        """
        try:
            # Filter and validate queryset
            queryset = AttendanceLog.objects.all()
            queryset = self.filter_queryset(queryset)

            # Aggregate top 5 employees
            top_5_employees = (
                queryset
                .values('applied_by__username')
                .annotate(total_duration=Sum('duration'))
                .order_by('-total_duration')[:5]
            )

            if not top_5_employees:
                return Response({"message": "No attendance data found for the given period."}, status=status.HTTP_200_OK)

            # Prepare response data
            result = []
            for employee in top_5_employees:
                total_duration_hours = employee['total_duration'].total_seconds() / 3600  # Convert seconds to hours
                result.append({
                    "employee": employee['applied_by__username'],
                    "total_duration_hours": round(total_duration_hours, 2)
                })

            # Calculate total working duration
            total_working_duration = self.calculate_working_duration(
                year=int(request.query_params['year']),
                month=int(request.query_params.get('month', 0))
            )

            response_data = {
                "top_5_employees": result,
                "total_working_duration_hours": total_working_duration
            }
            return Response(response_data, status=status.HTTP_200_OK)

        except ValidationError as ve:
            logging.error(f" BAD request{str(ve)}")
            return Response({"error": ve.detail}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logging.error(f"An unexpected error occurred: {str(e)}")
            return Response({"error": f"An unexpected error occurred: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

from django.http import JsonResponse
from django.views import View
from django.db.models import Sum
from datetime import timedelta

class Top5EmployeesView(View):
    def get(self, request, year):
        # Get holidays for the specified year
        holidays = Holiday.objects.filter(start_date__year=year)

        # Initialize a dictionary to store the total working hours per employee per month
        top_5_data = {month: [] for month in range(1, 13)}  # For each month, store top 5 employees

        for month in range(1, 13):
            # Filter AttendanceLog for each month, considering holidays and weekends
            monthly_data = (
                AttendanceLog.objects
                .filter(start_date__year=year, start_date__month=month)
                .exclude(start_date__week_day=7)  # Exclude Sundays
                .exclude(start_date__in=holidays.values('start_date'))  # Exclude holidays
                .values('applied_by__username')  # Use username as identifier
                .annotate(total_duration=Sum('duration'))
                .order_by('-total_duration')[:5]  # Get top 5 employees for the current month
            )

            # Store the data for the top 5 employees for the current month
            for record in monthly_data:
                employee_id = record['applied_by__username']
                total_duration_hours = record['total_duration'].total_seconds() / 3600  # Convert to hours

                # Only include employees with non-zero total duration
                if total_duration_hours > 0:
                    top_5_data[month].append({
                        'employee_id': employee_id,
                        'total_duration_hours': round(total_duration_hours, 2)
                    })

        # Prepare data for the response
        data = {
            'labels': ["JAN", "FEB", "MAR", "APR", "MAY", "JUN", "JUL", "AUG", "SEP", "OCT", "NOV", "DEC"],  # Months
            'datasets': []
        }

        employees = {}  # Keep track of employees and their data across all months

        # Now structure the data for the response
        for month, employees_data in top_5_data.items():
            for employee in employees_data:
                employee_id = employee['employee_id']
                total_duration_hours = employee['total_duration_hours']

                if employee_id not in employees:
                    employees[employee_id] = {
                        'label': employee_id,  # Use employee's username as label
                        'monthly_duration': []  # Only store months with non-zero duration
                    }

                # Add the current month and its working hours
                employees[employee_id]['monthly_duration'].append(total_duration_hours)

        # Now structure the data for the response
        for employee in employees.values():
            data['datasets'].append({
                'label': employee['label'],
                'data': employee['monthly_duration'],
                'borderColor': '#1F3BB3',  # Use a consistent color for all employees
                'fill': False
            })
        return JsonResponse(data)
