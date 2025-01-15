from django.urls import path
from django.shortcuts import render
from hrms_app.views import views,api_views,auth_views,report_view


class CustomSite:
    def __init__(self):
        self._registry = {}

    def register_view(self, url, view, name=None):
        wrapped_view = self.wrap_view(view)
        self._registry[url] = (wrapped_view, name)

    def has_permission(self, user, view):
        # sourcery skip: assign-if-exp, boolean-if-exp-identity, reintroduce-else
        if hasattr(view, 'permission_required'):
            permission = view.permission_required
            if user.has_perm(permission) or user.groups.filter(permissions__codename=permission.split('.')[-1]).exists():
                return True
            return False
        return True

    def wrap_view(self, view):
        def view_wrapper(request, *args, **kwargs):
            if not self.has_permission(request.user, view):
                return render(request, '403.html', status=403)
            return view.as_view()(request, *args, **kwargs)
        return view_wrapper

    def get_urls(self):
        urlpatterns = []
        for url, (view, name) in self._registry.items():
            if name:
                urlpatterns.append(path(url, view, name=name))
            else:
                urlpatterns.append(path(url, view))
        return urlpatterns

site = CustomSite()

app_name = 'hrms'
site.register_view('dashboard', views.HomePageView, name='dashboard')
site.register_view('login/', auth_views.LoginView, name='login')
site.register_view('logout/', auth_views.LogoutView, name='logout')
site.register_view('reset-password/', auth_views.PasswordResetView, name='reset_password')
site.register_view('reset-password-done/', auth_views.PasswordResetDoneView, name='password_reset_done')
site.register_view('reset-password-complete/', auth_views.PasswordResetCompleteView, name='password_reset_complete')
site.register_view('reset-password-confirm/<uidb64>/<token>/', auth_views.PasswordResetConfirmView, name='password_reset_confirm')
site.register_view('password-change/', views.ChangePasswordView, name='password_change')
site.register_view('password-change-done/', auth_views.PasswordChangeDoneView, name='password_change_done')
site.register_view('leave-tracker/', views.LeaveTrackerView, name='leave_tracker')
site.register_view('', views.EventPageView, name='calendar')
site.register_view('attendance/<slug:slug>/', views.EventDetailPageView, name='event_detail')
site.register_view('attendance-log/<slug:slug>/', views.AttendanceLogActionView, name='attendance_log_action')
site.register_view('attendance-regularization/', views.AttendanceLogListView, name='regularization')
site.register_view('profile/', views.ProfilePageView, name='profile')
site.register_view('leave/apply/<int:leave_type>/', views.ApplyOrUpdateLeaveView, name='apply_leave_with_id')
site.register_view('leave/edit/<slug:slug>/', views.ApplyOrUpdateLeaveView, name='update_leave')
site.register_view('leave/<slug:slug>/', views.LeaveApplicationDetailView, name='leave_application_detail')
site.register_view('leave/<slug:slug>/update', views.LeaveApplicationUpdateView, name='leave_application_update')
site.register_view('delete/<str:model_name>/<int:pk>/', views.GenericDeleteView, name='generic_delete')
site.register_view('leave-transaction/', views.LeaveTransactionCreateView, name='leave_transaction_create'),
site.register_view('leave-balance-update/', views.LeaveBalanceUpdateView, name='leave_bal_up'),
site.register_view('tour-tracker/', views.TourTrackerView, name='tour_tracker')
site.register_view('apply-tour/', views.ApplyTourView, name='apply_tour')
site.register_view('tour/<slug:slug>/', views.TourApplicationDetailView, name='tour_application_detail')
site.register_view('tour/<slug:slug>/update', views.TourApplicationUpdateView, name='tour_application_update')
site.register_view('tour/<slug:slug>/pdf', views.GenerateTourPDFView, name='generate_tour_pdf')
# site.register_view('tour/<slug:slug>/pdf/', views.UploadBillView, name='upload_bill')
site.register_view('employees/', views.EmployeeListView, name='employees')
site.register_view('employee-profile/<int:pk>/', views.EmployeeProfileView, name='employee_profile')

###############################################################################################
######                                Reports URLS                                        #####
###############################################################################################
site.register_view('attendance-report/', report_view.MonthAttendanceReportView, name='attendance_report')
site.register_view('detailed-attendance-report/', report_view.DetailedMonthlyPresenceView, name='detailed_attendance_report')
