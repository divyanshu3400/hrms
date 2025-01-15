from django.contrib import admin
from django.urls import path, include,re_path
from hrms_app.views.api_views import *
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,TokenVerifyView
)
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'attendance-settings', AttendanceSettingViewSet)
router.register(r'attendance-status-colors', AttendanceStatusColorViewSet)
router.register(r'holidays', HolidayViewSet)
router.register(r'attendance-logs', AttendanceLogViewSet,basename='attendance-logs')
router.register(r'leave-openings', UserLeaveOpeningsViewSet, basename='user-leave-openings')
router.register(r'leavetype', LeaveTypeViewSet, basename='leavetype')
router.register(r'user', UserViewSet, basename='user')
router.register(r'device', DeviceInformationViewSet, basename='device')
router.register(r'tours', UserTourViewSet, basename='user-tour')
router.register(r'leave-applications', LeaveApplicationViewSet, basename='leaveapplication')

urlpatterns = [
    path('', include(router.urls)),
    path("token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path('token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    path('personal-details/', PersonalDetailsView.as_view(), name='personal-details'),
    path('employee-shifts/', EmployeeShiftView.as_view(), name='employee-shifts'),
    path('attendance-choices/', AttendanceChoicesView.as_view(), name='attendance-choices'),
    path('current_user/', CurrentUserAPIView.as_view(), name='current_user'),
    path('users/<int:pk>/', CustomUserDetailAPIView.as_view(), name='custom_user_detail'),
    path('notifications/', UserMonthlyNotificationsListView.as_view(), name='user_notifications'),
    path('notifications/<int:id>/', UpdateNotificationStatusView.as_view(), name='update-notification-status'),
    path("execute-populate-attendance/", ExecutePopulateAttendanceView.as_view(), name="execute_populate_attendance"),
    path('attendance-aggregation/', Top5EmployeesDurationAPIView.as_view(), name='attendance-aggregation'),
    path('get_top_5_employees/<int:year>/', Top5EmployeesView.as_view(), name='get_top_5_employees'),

]
