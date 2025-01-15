# Standard library imports
import json
import logging
from datetime import datetime
from urllib.parse import urlparse
from hrms_app.utility.leave_utils import format_date
from django.utils.http import urlencode

# Third-party imports
from django.http import HttpResponseForbidden, HttpResponseRedirect, JsonResponse
from django.contrib import messages
from django.views.generic import (
    FormView,
    DetailView,
    CreateView,
    TemplateView,
    UpdateView,
    DeleteView,
    ListView,
)
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.apps import apps
from django_filters.views import FilterView
from django_tables2.views import SingleTableMixin
from django.urls import reverse, reverse_lazy
from django.core.exceptions import PermissionDenied
from django.db import IntegrityError, transaction
from django.core.files.storage import FileSystemStorage, default_storage
from django.forms.models import model_to_dict
from django.views import View
from django.core.files.base import ContentFile
from django.utils.timezone import now, localtime
from django.contrib.messages.views import SuccessMessageMixin
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from django.views.generic.edit import ModelFormMixin

# Local imports
from hrms_app.hrms.form import *
from hrms_app.views.mixins import LeaveListViewMixin
from hrms_app.table_classes import (
    UserTourTable,
    LeaveApplicationTable,
    AttendanceLogTable,
)
from django.contrib.auth import get_user_model
from django.views.decorators.csrf import csrf_exempt

User = get_user_model()
logger = logging.getLogger(__name__)
from hrms_app.tasks import push_notification

def custom_permission_denied(request, exception=None):
    error_message = (
        str(exception)
        if exception
        else "You do not have permission to access this page."
    )
    return render(request, "403.html", {"error_message": error_message})


class HomePageView(LoginRequiredMixin, TemplateView):
    template_name = "admin/index.html"
    title = _("Dashboard")

    def dispatch(self, request, *args, **kwargs):
        # Check if the user is a superuser
        if not (request.user.is_superuser or request.user.is_staff):
            return HttpResponseForbidden(
                "You do not have permission to access this page."
            )
        return super().dispatch(request, *args, **kwargs)

    def get_employee_wishing(self):
        today = now().date()
        employees = PersonalDetails.objects.filter(
            models.Q(birthday__month=today.month, birthday__day=today.day)
            | models.Q(marriage_ann__month=today.month, marriage_ann__day=today.day)
            | models.Q(doj__month=today.month, doj__day=today.day)
        )

        light_colors = [
            "bg-light-blue",
            "bg-light-pink",
            "bg-light-yellow",
            "bg-light-green",
            "bg-light-coral",
            "bg-light-cyan",
            "bg-light-lavender",
        ]

        for employee in employees:
            events = []
            if (
                employee.birthday
                and employee.birthday.month == today.month
                and employee.birthday.day == today.day
            ):
                events.append("🎉 Happy Birthday! 🎉")
            if (
                employee.marriage_ann
                and employee.marriage_ann.month == today.month
                and employee.marriage_ann.day == today.day
            ):
                events.append("💍 Happy Marriage Anniversary! 💍")
            if (
                employee.doj
                and employee.doj.month == today.month
                and employee.doj.day == today.day
            ):
                events.append("🎊 Happy Job Anniversary! 🎊")
            employee.events = events

            # Assign a random light color to each employee
            employee.bg_color = random.choice(light_colors)

        return employees

    def get_context_data(self, **kwargs):
        """Add custom context data for the dashboard."""
        context = super().get_context_data(**kwargs)
        context["current_date"] = datetime.now()
        push_notification(user=self.request.user,head="Hello There",body="Testing the webpush notification",url="http://hr.kasheemilk.com:7777/dashboard")
        # Fetch all users to pass in the context
        users = User.objects.all()  # Adjust this if you want to filter the users
        context["users"] = users

        urls = [
            ("dashboard", {"label": "Dashboard"}),
        ]
        context["urls"] = urls
        context["form"] = PopulateAttendanceForm()
        context.update(
            {
                "title": self.title,
                "employees": self.get_employee_wishing(),
            }
        )
        return context

    def get(self, request, *args, **kwargs):
        """Handle GET requests."""
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        """Handle POST requests."""
        return super().post(request, *args, **kwargs)


class EmployeeProfileView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    template_name = "hrms_app/profile.html"
    model = CustomUser
    context_object_name = "employee"
    permission_required = "hrms_app.view_employeeprofileview"

    def test_func(self):
        return self.get_object() == self.request.user or self.request.user.is_staff

    def get_object(self, queryset=None):
        user_id = self.kwargs.get("pk")
        if user_id:
            return get_object_or_404(CustomUser, id=user_id)
        return self.request.user

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        print(self.request.user)
        context["current_date"] = datetime.now()
        urls = [
            ("dashboard", {"label": "Dashboard"}),
        ]
        context["urls"] = urls
        return context

    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class AboutPageView(TemplateView):
    template_name = "hrms_app/calendar.html"


class LeaveTrackerView(LoginRequiredMixin, SingleTableMixin, FilterView):
    template_name = "hrms_app/leave-tracker.html"
    model = LeaveApplication
    permission_action = "view"
    title = _("Leave Tracker")

    def dispatch(self, request, *args, **kwargs):
        """Check if the user has the required permission dynamically."""
        opts = self.model._meta
        perm = f"{opts.app_label}.{self.permission_action}_{opts.model_name}"
        if not request.user.has_perm(perm):
            logger.warning(
                f"Permission denied for user {request.user}. Required: {perm}"
            )
            raise PermissionDenied(
                "You do not have permission to access this resource."
            )

        return super().dispatch(request, *args, **kwargs)

    def get_table_class(self):
        # Dynamically define table columns based on session data or defaults
        class DynamicLeaveApplicationTable(LeaveApplicationTable):
            class Meta(LeaveApplicationTable.Meta):
                # Get selected columns from session or use defaults
                selected_columns = self.request.session.get(
                    "selected_columns", ["appliedBy", "status", "startDate", "endDate"]
                )
                fields = selected_columns

        return DynamicLeaveApplicationTable

    def get_filtered_leaves(self, user, form):
        """Apply filters to the leave applications."""
        try:
            employee_leaves = LeaveApplication.objects.filter(
                appliedBy__in=user.employees.all()
            )
            if form.is_valid():
                status = form.cleaned_data.get("status")
                from_date = form.cleaned_data.get("fromDate")
                to_date = form.cleaned_data.get("toDate")
                if status:
                    employee_leaves = employee_leaves.filter(status=status)
                if from_date:
                    employee_leaves = employee_leaves.filter(startDate__gte=from_date)
                if to_date:
                    employee_leaves = employee_leaves.filter(endDate__lte=to_date)
            else:
                messages.warning(self.request, "Invalid filter data provided.")
            return employee_leaves
        except ValidationError as ve:
            logger.warning(f"Validation error while filtering leaves: {ve}")
            messages.error(
                self.request,
                "There was an issue processing your filter. Please try again.",
            )
            return LeaveApplication.objects.none()
        except Exception as e:
            logger.exception(f"Unexpected error while filtering leaves: {e}")
            messages.error(
                self.request, "An unexpected error occurred. Please contact support."
            )
            return LeaveApplication.objects.none()

    def get_queryset(self):
        """Filter tours based on the logged-in user's tours and their employees' tours."""
        user = self.request.user
        user_leaves = LeaveApplication.objects.filter(appliedBy=user)

        # Get the search query parameter (if any)
        search_term = self.request.GET.get("q", "").strip()
        if search_term:
            user_leaves = user_leaves.filter(
                Q(appliedby__username__icontains=search_term)
                | Q(
                    appliedby__first_name__icontains=search_term
                )  # Search by first name
                | Q(appliedby__last_name__icontains=search_term)
                | Q(
                    from_destination__icontains=search_term
                )  # Search by from_destination
                | Q(to_destination__icontains=search_term)
            )

        return user_leaves

    def get_context_data(self, **kwargs):
        """Prepare the context for the template."""
        context = super().get_context_data(**kwargs)
        user = self.request.user

        # Initialize filter form
        form = FilterForm(self.request.GET)

        try:
            # Prepare leave balances and filtered leaves
            combined_leaves = self.get_filtered_leaves(user, form)
            employee_leaves = combined_leaves.filter(appliedBy__in=user.employees.all())
            context.update(
                {
                    "current_date": now(),
                    "form": form,
                    "employee_leaves": [
                        {
                            "leaveApplication": leave,
                            "start_date": leave.startDate.strftime("%Y-%m-%d"),
                            "end_date": leave.endDate.strftime("%Y-%m-%d"),
                        }
                        for leave in employee_leaves
                    ],
                    "pending_leave_count": LeaveApplication.objects.filter(
                        appliedBy=user, status=settings.PENDING
                    ).count(),
                    "urls": [
                        ("dashboard", {"label": "Dashboard"}),
                        ("leave_tracker", {"label": "Leave Tracker"}),
                    ],
                }
            )
            all_columns = [
                field.name
                for field in LeaveApplication._meta.fields
                if field.name not in ["id", "slug", "reason"]
            ]
            selected_columns = self.request.session.get(
                "selected_columns", ["appliedBy", "status", "startDate", "endDate"]
            )
            context["all_columns"] = all_columns
            context["selected_columns"] = selected_columns
            context["title"] = self.title
        except Exception as e:
            logger.exception(f"Unexpected error in context preparation: {e}")
            messages.error(
                self.request,
                "An error occurred while loading the page. Please try again later.",
            )

        return context


def save_column_preferences(request):
    if request.method == "POST":
        data = json.loads(request.body)
        selected_columns = data.get("selected_columns", [])
        request.session["selected_columns"] = selected_columns
        return JsonResponse({"status": "success", "selected_columns": selected_columns})
    return JsonResponse({"status": "error"}, status=400)


class ApplyOrUpdateLeaveView(
    LoginRequiredMixin, SuccessMessageMixin, ModelFormMixin, FormView
):
    model = LeaveApplication
    form_class = LeaveApplicationForm
    template_name = "hrms_app/apply-leave.html"
    success_message_create = _("Leave applied successfully.")
    success_message_update = _("Leave updated successfully.")
    permission_action_create = "add"
    permission_action_update = "change"
    title = _("Create Update Leave Application")

    def dispatch(self, request, *args, **kwargs):
        """Check if the user has permission dynamically for the model."""
        self.object = None
        if "slug" in kwargs:  # 'slug' determines update vs. create
            self.object = self.get_object()
            permission_action = self.permission_action_update
        else:
            permission_action = self.permission_action_create

        opts = self.model._meta
        perm = f"{opts.app_label}.{permission_action}_{opts.model_name}"
        if not request.user.has_perm(perm):
            raise PermissionDenied("You do not have permission to perform this action.")
        return super().dispatch(request, *args, **kwargs)

    def get_form(self, form_class=None):
        """Retrieve the form instance with the correct data."""
        if form_class is None:
            form_class = self.get_form_class()
        # Just pass the form kwargs without adding instance again
        return form_class(**self.get_form_kwargs())

    def get_form_kwargs(self):
        """Pass additional data to the form."""
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        kwargs["leave_type"] = (
            self.object.leave_type.id if self.object else self.kwargs.get("leave_type")
        )

        return kwargs

    def form_valid(self, form):
        """Handle successful form submission."""
        leave_application = form.save(commit=False)
        leave_application.appliedBy = self.request.user
        leave_application.save()
        if self.object:  # Update
            success_message = self.success_message_update
        else:  # Create
            success_message = self.success_message_create
        messages.success(self.request, success_message)
        # Redirect to the next URL if provided, or fallback to leave tracker
        next_url = self.request.POST.get("next")
        if next_url and urlparse(next_url).netloc == "":
            return redirect(next_url)
        return redirect(reverse_lazy("leave_tracker"))

    def form_invalid(self, form):
        """Handle form submission failure."""
        context = self.get_context_data(form=form)
        error_message = (
            _("Leave update failed. Please correct the errors below.")
            if self.object
            else _("Leave application failed. Please correct the errors below.")
        )
        messages.error(self.request, error_message)
        return self.render_to_response(context)

    def get_context_data(self, **kwargs):
        """Prepare context data for the template."""
        context = super().get_context_data(**kwargs)
        leave_type_id = (
            self.object.leave_type.id if self.object else self.kwargs.get("leave_type")
        )

        # Fetch leave balance for the specified leave type
        leave_balance = LeaveBalanceOpenings.objects.filter(
            user=self.request.user,
            leave_type_id=leave_type_id,
            year=timezone.now().year,
        ).first()

        # Add data to the context
        context.update(
            {
                "leave_balance": leave_balance,
                "form": kwargs.get(
                    "form",
                    LeaveApplicationForm(
                        instance=self.object,  # Ensure instance is passed
                        user=self.request.user,
                        leave_type=leave_type_id,
                    ),
                ),
                "title": self.title,
                "urls": [
                    ("dashboard", {"label": "Dashboard"}),
                    ("leave_tracker", {"label": "Leave Tracker"}),
                ],
            }
        )
        return context

    def get_object(self):
        """Retrieve the object for update."""
        if "slug" in self.kwargs:
            return LeaveApplication.objects.get(slug=self.kwargs["slug"])
        return None


class GenericDeleteView(LoginRequiredMixin, SuccessMessageMixin, DeleteView):
    template_name = "hrms_app/confirm_delete.html"
    success_message = "Deleted successfully."
    permission_action = "delete"

    def dispatch(self, request, *args, **kwargs):
        """Check if the user has permission dynamically for the model."""
        self.model = self.get_model()
        opts = self.model._meta
        perm = f"{opts.app_label}.{self.permission_action}_{opts.model_name}"
        if not request.user.has_perm(perm):
            raise PermissionDenied("You do not have permission to delete this item.")
        return super().dispatch(request, *args, **kwargs)

    def get_model(self):
        """Get the model class based on the URL parameter."""
        model_name = self.kwargs.get("model_name")
        return apps.get_model("hrms_app", model_name)

    def get_object(self):
        """Get the object to be deleted."""
        model = self.get_model()
        return get_object_or_404(model, pk=self.kwargs.get("pk"))

    def get_success_url(self):
        """Get the URL to redirect to after successful deletion."""
        # Extract 'next' parameter from the request
        # next_url = self.request.GET.get('next')
        # if next_url:
        #     # Validate the 'next' URL to ensure it's safe
        #     parsed_url = urlparse(next_url)
        #     if parsed_url.netloc == "" or parsed_url.netloc == self.request.get_host():
        #         return next_url
        # # Fallback to a default URL
        return reverse_lazy("calendar")

    def delete(self, request, *args, **kwargs):
        """Handle successful deletion."""
        response = super().delete(request, *args, **kwargs)
        messages.success(self.request, self.success_message)
        return response

    def get_context_data(self, **kwargs):
        """Prepare context data for the template."""
        context = super().get_context_data(**kwargs)
        object_to_delete = self.get_object()

        # Dynamically fetch related logs or objects
        related_objects = self.get_related_objects(object_to_delete)

        # Pass the related objects and data to the context
        context["object_name"] = self.model._meta.verbose_name
        context["related_objects"] = related_objects
        context["cancel_url"] = self.get_success_url()
        return context

    def get_related_objects(self, object_to_delete):
        """Dynamically fetch related objects."""
        related_objects = []

        for rel in object_to_delete._meta.related_objects:
            if hasattr(rel, "related_model"):  # Check if the model has a related model
                related_model = rel.related_model
                accessor_name = rel.get_accessor_name()  # Correct field accessor name

                # Fetch related objects using the accessor name
                related_data = getattr(object_to_delete, accessor_name).all()
                for related_item in related_data:
                    related_objects.append(
                        {
                            "model_name": related_model._meta.verbose_name,  # Add verbose name here
                            "item": related_item,
                        }
                    )

        return related_objects


class LeaveApplicationUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = LeaveApplication
    form_class = LeaveStatusUpdateForm
    template_name = "hrms_app/leave_application_detail.html"
    permission_required = "hrms_app.change_leaveapplication"
    permission_denied_message = (
        "You do not have permission to update the LeaveApplication."
    )

    def test_func(self):
        return self.request.user.has_perm(self.permission_required)

    def get_object(self, queryset=None):
        return get_object_or_404(LeaveApplication, slug=self.kwargs.get("slug"))

    def update_leave_balance(self, leave_application):
        leave_balance = LeaveBalanceOpenings.objects.filter(
            user=leave_application.appliedBy,
            leave_type=leave_application.leave_type,
            year=localtime(leave_application.startDate).year,
        ).first()
        if leave_balance:
            if leave_application.status == settings.APPROVED:
                leave_balance.remaining_leave_balances -= leave_application.usedLeave
            elif leave_application.status == settings.CANCELLED:
                leave_balance.remaining_leave_balances += leave_application.usedLeave
            leave_balance.save()

    def form_valid(self, form):
        response = super().form_valid(form)
        leave_application = form.instance
        action_by = self.request.user
        self.update_leave_balance(leave_application)
        LeaveLog.create_log(leave_application, action_by, leave_application.status)
        messages.success(
            self.request,
            _(f"Leave application {leave_application.status} successfully"),
        )
        return response

    def get_success_url(self):
        return reverse_lazy(
            "leave_application_detail", kwargs={"slug": self.object.slug}
        )


from django.core.exceptions import ObjectDoesNotExist

class LeaveApplicationDetailView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    model = LeaveApplication
    template_name = "hrms_app/leave_application_detail.html"
    context_object_name = "leave_application"
    permission_denied_message = _("You do not have permission to access this page.")
    permission_required = "hrms_app.view_leaveapplication"
    title = _("Leave Application Detail")

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        if not self.test_func():
            raise PermissionDenied(self.permission_denied_message)
        return super().dispatch(request, *args, **kwargs)

    def test_func(self):
        return self.request.user.has_perm(self.permission_required)

    def get_object(self, queryset=None):
        try:
            leave_application = super().get_object(queryset)
            if self.has_permission_to_view(leave_application):
                return leave_application
            raise PermissionDenied(self.permission_denied_message)
        except ObjectDoesNotExist:
            messages.error(self.request, _("Leave application does not exist, perhaps it was deleted."))
            return redirect('calendar')  # Replace 'dashboard' with the name of your dashboard URL

    def has_permission_to_view(self, leave_application):
        user = self.request.user
        return (
            leave_application.appliedBy == user
            or user.is_superuser
            or user.is_staff
            or leave_application.appliedBy.reports_to == user
            or user.personal_detail.designation.department.department == "admin"
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        leave_application = self.get_object()
        context.update(
            {
                "is_manager": self.is_manager(leave_application),
                "status_form": self.get_status_form(),
                "leave_balance": self.get_leave_type_balance(leave_application),
                "delete_url": self.get_delete_url(),
                "edit_url": self.get_edit_url(),
                "urls": self.get_breadcrumb_urls(leave_application),
                "title": self.title,
            }
        )
        return context

    def is_manager(self, leave_application):
        return self.request.user == leave_application.appliedBy.reports_to

    def get_status_form(self):
        return LeaveStatusUpdateForm(user=self.request.user, instance=self.object)

    def get_leave_type_balance(self, leave_application):
        return LeaveBalanceOpenings.objects.filter(
            user=leave_application.appliedBy,
            year=localtime(leave_application.startDate).date().year,
            leave_type=leave_application.leave_type,
        ).first()

    def get_delete_url(self):
        return reverse(
            "generic_delete",
            kwargs={"model_name": self.model.__name__, "pk": self.object.pk},
        )

    def get_edit_url(self):
        return reverse("update_leave", kwargs={"slug": self.object.slug})

    def get_breadcrumb_urls(self, leave_application):
        return [
            ("dashboard", {"label": "Dashboard"}),
            ("leave_tracker", {"label": "Leave Tracker"}),
            (
                "leave_application_detail",
                {
                    "label": f"{leave_application.applicationNo}",
                    "slug": leave_application.slug,
                },
            ),
        ]


class LeaveApplicationListView(View, LeaveListViewMixin):
    START_LEAVE_TYPE_CHOICES = {
        "1": "Full Day",
        "2": "First Half (Morning)",
        "3": "Second Half (Afternoon)",
    }

    def get(self, request):
        if not request.user.is_authenticated:
            return JsonResponse({"error": "User not authenticated"}, status=401)

        leave_applications = [
            {
                "name": f"{leaveApplication.appliedBy.first_name} {leaveApplication.appliedBy.last_name}",
                "applicationNo": leaveApplication.applicationNo,
                "leave_type": leaveApplication.leave_type.leave_type,
                "startDate": format_date(leaveApplication.startDate),
                "startDayChoice": self.START_LEAVE_TYPE_CHOICES.get(
                    leaveApplication.startDayChoice, leaveApplication.startDayChoice
                ),
                "endDate": format_date(leaveApplication.endDate),
                "endDayChoice": self.START_LEAVE_TYPE_CHOICES.get(
                    leaveApplication.endDayChoice, leaveApplication.endDayChoice
                ),
                "usedLeave": leaveApplication.usedLeave,
                "status": leaveApplication.status.capitalize(),
            }
            for leaveApplication in request.user.leaves.all()
        ]

        data = {
            "header": self.get_headers(),  # Assuming get_headers() is still applicable
            "data": leave_applications,
        }

        return JsonResponse(data)


class EventPageView(LoginRequiredMixin, TemplateView):
    template_name = "hrms_app/calendar.html"
    model = AttendanceLog
    title = _("Attendance Log")

    def get_context_data(self, **kwargs):
        """Prepare the context for the template."""
        context = super().get_context_data(**kwargs)
        initial_data = {"employee": self.request.user}
        form = EmployeeChoicesForm(self.request.GET or initial_data)

        if form.is_valid():
            employee = form.cleaned_data.get("employee")
        else:
            employee = self.request.user

        employee = self.request.user if employee is None else employee

        context.update(
            {
                "current_date": now(),
                "form": form,
                "employee": employee,
                "title": self.title,
                "urls": [
                    ("dashboard", {"label": "Dashboard"}),
                    ("calendar", {"label": "Attendance Calendar"}),
                ],
            }
        )
        return context


class EventDetailPageView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = AttendanceLog
    template_name = "hrms_app/event_detail.html"
    form_class = AttendanceLogForm
    slug_field = "slug"
    slug_url_kwarg = "slug"
    title = _("Attendance Log")
    permission_required = "hrms_app.change_attendancelog"

    def dispatch(self, request, *args, **kwargs):
        # Check if the user is authenticated
        if not request.user.is_authenticated:
            return self.handle_no_permission()

        # Perform the permission check
        if not self.test_func():
            raise PermissionDenied(_("You do not have permission to access this page."))

        return super().dispatch(request, *args, **kwargs)

    def test_func(self):
        # Determine the required permission dynamically based on the HTTP method
        if self.request.method in ["GET"]:
            permission_required = (
                f"{self.model._meta.app_label}.view_{self.model._meta.model_name}"
            )
        elif self.request.method in ["POST", "PUT", "PATCH"]:
            permission_required = (
                f"{self.model._meta.app_label}.change_{self.model._meta.model_name}"
            )
        else:
            # Default to the permission specified in the class
            permission_required = self.permission_required

        return self.request.user.has_perm(permission_required)

    def form_valid(self, form):
        count = AttendanceLog.objects.filter(
            applied_by=self.request.user,
            start_date__date__month=self.object.start_date.date().month,
        ).filter(
            Q(regularized=True) | Q(is_submitted=True)
        ).count()
        if count >= 3:
            messages.error(
                self.request, _("Your already have applied regularization 3 times.")
            )
        else:
            form.instance.is_submitted = True
            self.object = form.save()
            self.object.add_action(
                action="Submitted regularization",
                performed_by=self.request.user,
                comment=form.instance.reason,
            )
            messages.success(self.request, _("Regularization Updated Successfully"))
        return HttpResponseRedirect(
            reverse("event_detail", kwargs={"slug": self.object.slug})
        )

    def form_invalid(self, form):
        return self.render_to_response(self.get_context_data(form=form))

    def get_object(self, queryset=None):
        attendance_log = super().get_object(queryset)
        user = self.request.user
        if (
            attendance_log.applied_by == user
            or attendance_log.applied_by.reports_to == user
            or self.request.user.is_staff
            or self.request.user.is_superuser
            or user.personal_detail.designation.department.department == "admin"
        ):
            return attendance_log
        raise PermissionDenied()

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        attendance_log = self.get_object()
        kwargs["user"] = self.request.user
        kwargs["is_manager"] = self.request.user == attendance_log.applied_by.reports_to
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        attendance_log = self.get_object()
        context["is_manager"] = (
            self.request.user == attendance_log.applied_by.reports_to
        )
        urls = [
            ("dashboard", {"label": "Dashboard"}),
            ("calendar", {"label": "Attendance"}),
            (
                "event_detail",
                {"label": f"{attendance_log.title}", "slug": attendance_log.slug},
            ),
        ]
        context["urls"] = urls
        context["action_form"] = AttendanceLogActionForm()
        context.update(
            {
                "title": self.title,
                "subtitle": self.get_object().slug,
            }
        )
        return context


class AttendanceLogActionView(LoginRequiredMixin, View):
    def fetch_static_data(self):
        """Fetch static data used in attendance calculations."""
        return {
            "half_day_color": AttendanceStatusColor.objects.get(
                status=settings.HALF_DAY
            ),
            "present_color": AttendanceStatusColor.objects.get(status=settings.PRESENT),
            "absent_color": AttendanceStatusColor.objects.get(status=settings.ABSENT),
            "asettings": AttendanceSetting.objects.first(),
        }

    def get_users(self, username):
        """Retrieve users based on username or all users if not specified."""
        queryset = User.objects.all().select_related("personal_detail")
        return queryset.filter(username=username) if username else queryset

    def parse_dates(self, from_date_str, to_date_str):
        """Parse string dates into timezone-aware datetime objects."""
        parse_date = lambda d: (
            make_aware(datetime.strptime(d, "%Y-%m-%d")) if d else None
        )
        return parse_date(from_date_str), parse_date(to_date_str)

    def get_user_shift(self, user):
        """Retrieve the shift timing for a given user."""
        emp_shift = (
            EmployeeShift.objects.filter(employee=user)
            .select_related("shift_timing")
            .first()
        )
        return emp_shift.shift_timing if emp_shift else None

    def handle_attendance_update(self, log, form_data, static_data):
        """Update attendance log with approval adjustments."""
        AttendanceLogHistory.objects.create(
            attendance_log=log,
            previous_data=make_json_serializable(model_to_dict(log)),
            modified_by=self.request.user,
        )

        reason = form_data["reason"]
        if log.reg_status == settings.EARLY_GOING:
            log.end_date = log.to_date
        elif log.reg_status == settings.LATE_COMING:
            log.start_date = log.from_date
        log.save()
        from hrms_app.hrms.managers import AttendanceStatusHandler

        status_handler = AttendanceStatusHandler(
            self.get_user_shift(log.applied_by),
            static_data["asettings"].full_day_hours,
            static_data["half_day_color"],
            static_data["present_color"],
            static_data["absent_color"],
        )

        log_start_date = localtime(log.start_date)
        log_end_date = localtime(log.end_date)
        total_duration = log_end_date - log_start_date
        user_expected_logout_time = log_start_date + timedelta(
            hours=static_data["asettings"].full_day_hours
        )

        status_data = status_handler.determine_attendance_status(
            log_start_date,
            log_end_date,
            total_duration,
            user_expected_logout_time.time(),
            user_expected_logout_time,
        )
        (
            log.att_status,
            log.color_hex,
            log.reg_status,
            log.is_regularisation,
            log.from_date,
            log.to_date,
            log.reg_duration,
            log.status,
            log.att_status_short_code,
        ) = status_data
        total_minutes = total_duration.total_seconds() // 60

        # Calculate hours and minutes
        hours = total_minutes // 60
        minutes = total_minutes % 60
        time_difference = f"{int(hours):02}:{int(minutes):02}"
        log.duration = time_difference
        log.regularized = True
        log.save()
        log.approve(action_by=self.request.user, reason=reason)
        return _("Attendance log approved and updated successfully.")

    def post(self, request, *args, **kwargs):
        action = request.POST.get("action")
        log_id = kwargs.get("slug")
        log = get_object_or_404(AttendanceLog, slug=log_id)
        form = AttendanceLogActionForm(request.POST)
        if form.is_valid():
            static_data = self.fetch_static_data()
            reason = form.cleaned_data["reason"]
            action_handlers = {
                "approve": lambda: self.handle_attendance_update(
                    log, form.cleaned_data, static_data
                ),
                "reject": lambda: log.reject(action_by=request.user, reason=reason),
                "recommend": lambda: log.recommend(
                    action_by=request.user, reason=reason
                ),
                "notrecommend": lambda: log.notrecommend(
                    action_by=request.user, reason=reason
                ),
            }

            if action in action_handlers:
                message = action_handlers[action]()
                messages.success(request, message)
            else:
                messages.error(request, _("Invalid action."))

            return HttpResponseRedirect(
                reverse("event_detail", kwargs={"slug": log.slug})
            )

        messages.error(request, _("Invalid action or form data."))
        return HttpResponseRedirect(reverse("event_detail", kwargs={"slug": log.slug}))


import json
from django.forms.models import model_to_dict
from django.core.serializers.json import DjangoJSONEncoder


def make_json_serializable(data):
    """Ensure data is JSON serializable."""
    return json.loads(json.dumps(data, cls=DjangoJSONEncoder))


class EventListView(View):
    def get(self, request, *args, **kwargs):
        user_id = request.GET.get("employee", self.request.user.id)
        try:
            user = User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return JsonResponse({"error": "User not found"}, status=404)

        holidays = Holiday.objects.all()
        attendances = AttendanceLog.objects.filter(applied_by=user)
        leave_applications = LeaveApplication.objects.filter(appliedBy=user)
        tour_applications = UserTour.objects.filter(applied_by=user)

        events_data = []
        # Adding holidays
        events_data.extend(
            [
                {
                    "id": holiday.pk,
                    "title": holiday.title,
                    # Combine date with midnight time to create a naive datetime object
                    "start": timezone.localtime(
                        timezone.make_aware(
                            datetime.combine(holiday.start_date, datetime.min.time())
                        )
                    ).isoformat(),
                    # Adjust the end date to be the next day and make it timezone-aware
                    "end": timezone.localtime(
                        timezone.make_aware(
                            datetime.combine(holiday.end_date, datetime.min.time())
                            + timezone.timedelta(days=1)
                        )
                    ).isoformat(),
                    "color": holiday.color_hex,
                    "url": "#!",
                }
                for holiday in holidays
            ]
        )

        # Adding tours
        events_data.extend(
            [
                {
                    "id": tour.slug,
                    "title": f"Tour -> {tour.approval_type}",
                    "start": timezone.localtime(
                        timezone.make_aware(
                            datetime.combine(tour.start_date, tour.start_time)
                        )
                    ).isoformat(),
                    "end": timezone.localtime(
                        timezone.make_aware(
                            datetime.combine(tour.end_date, tour.end_time)
                        )
                    ).isoformat(),
                    "url": reverse_lazy(
                        "tour_application_detail", kwargs={"slug": tour.slug}
                    ),
                }
                for tour in tour_applications
            ]
        )

        # Adding leave applications
        events_data.extend(
            [
                {
                    "id": leave.slug,
                    "title": f"{leave.leave_type.leave_type} {leave.status}",
                    "start": localtime(
                        leave.startDate
                    ),
                    "end": localtime(
                        leave.endDate
                    ),
                    "color": leave.leave_type.color_hex,
                    "url": reverse_lazy(
                        "leave_application_detail", kwargs={"slug": leave.slug}
                    ),
                }
                for leave in leave_applications
            ]
        )

        # Adding attendance logs
        for att in attendances:
            events_data.append(
                {
                    "id": att.slug,
                    "title": att.att_status,
                    "start": timezone.localtime(
                        att.start_date
                    ).isoformat(),  # Convert to local time
                    "end": timezone.localtime(
                        att.end_date
                    ).isoformat(),  # Convert to local time
                    "color": att.color_hex,
                    "url": reverse_lazy("event_detail", kwargs={"slug": att.slug}),
                }
            )
            if att.reg_status is not None:
                events_data.append(
                    {
                        "id": att.slug,
                        "title": att.reg_status,
                        "start": timezone.localtime(
                            att.start_date
                        ).isoformat(),  # Convert to local time
                        "end": timezone.localtime(
                            att.end_date
                        ).isoformat(),  # Convert to local time
                        "url": reverse_lazy("event_detail", kwargs={"slug": att.slug}),
                    }
                )
        return JsonResponse(events_data, safe=False)


from django_filters.views import FilterView

from hrms_app.hrms.filters import AttendanceLogFilter


class AttendanceLogListView(LoginRequiredMixin, SingleTableMixin, FilterView):
    model = AttendanceLog
    table_class = AttendanceLogTable
    template_name = "hrms_app/regularization.html"
    context_object_name = "attendance_logs"
    paginate_by = 100
    filterset_class = AttendanceLogFilter
    title = _("Regularizations")

    def filter_by_user_role(self, queryset):
        user = self.request.user

        if user.is_superuser or user.is_staff:
            return queryset
        elif hasattr(user, "employees"):
            return queryset.filter(
                Q(applied_by=user) | Q(applied_by__in=user.employees.all()),
                is_regularisation=True,
            )
        else:
            return queryset.filter(applied_by=user, is_regularisation=True)

    def get_queryset(self):
        queryset = super().get_queryset()
        return self.filter_by_user_role(queryset)

    def get_filterset(self, filterset_class):
        return filterset_class(
            self.request.GET, queryset=self.get_queryset(), user=self.request.user
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["filter"] = self.get_filterset(self.filterset_class)
        context.update({"title": self.title})
        return context


class ProfilePageView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    template_name = "hrms_app/profile.html"
    permission_required = "hrms_app.view_personaldetails"

    def test_func(self):
        return self.request.user.has_perm(self.permission_required)

    def get_context_data(self, **kwargs):
        pd = None
        if PersonalDetails.objects.filter(user=self.request.user).exists():
            pd = PersonalDetails.objects.get(user=self.request.user)
        print(self.request.user)
        context = super().get_context_data(**kwargs)
        context["current_date"] = datetime.now()
        context["pd"] = pd
        return context


class ChangePasswordView(LoginRequiredMixin, FormView):
    template_name = "hrms_app/change-password.html"
    form_class = ChangeUserPasswordForm
    success_url = reverse_lazy("login")
    error_message = "Error while changing the password. Please try again"

    def form_valid(self, form):
        custom_user = self.request.user
        custom_user.is_password_changed = True
        custom_user.save()
        form.save()
        messages.success(
            self.request,
            "Your password was changed successfully. Please Login again to continue...",
        )
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, self.error_message)
        return super().form_invalid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["error_message"] = self.error_message
        context["form_errors"] = self.get_form().errors  # Corrected line
        return context

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs


class TourTrackerView(LoginRequiredMixin, SingleTableMixin, FilterView):
    template_name = "hrms_app/tour-tracker.html"
    model = UserTour
    table_class = UserTourTable
    permission_action = "view"

    def dispatch(self, request, *args, **kwargs):
        """Check if the user has the required permission dynamically."""
        opts = self.model._meta
        perm = f"{opts.app_label}.{self.permission_action}_{opts.model_name}"
        if not request.user.has_perm(perm):
            raise PermissionDenied(
                "You do not have permission to access this resource."
            )
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        """Filter tours based on the logged-in user's tours and their employees' tours."""
        user = self.request.user
        # Get the user's own tours and the tours assigned to their employees
        user_tours = UserTour.objects.filter(applied_by=user)

        # Get the search query parameter (if any)
        search_term = self.request.GET.get("search", "").strip()

        if search_term:
            # Perform a case-insensitive search across multiple fields
            user_tours = user_tours.filter(
                Q(applied_by__username__icontains=search_term)  # Search by username
                | Q(
                    applied_by__first_name__icontains=search_term
                )  # Search by first name
                | Q(applied_by__last_name__icontains=search_term)  # Search by last name
                | Q(
                    from_destination__icontains=search_term
                )  # Search by from_destination
                | Q(to_destination__icontains=search_term)  # Search by to_destination
            )

        return user_tours

    def get_context_data(self, **kwargs):
        """Prepare the context for the template."""
        context = super().get_context_data(**kwargs)
        user = self.request.user
        form = FilterForm(self.request.GET)

        # Get the user's own tours
        user_tours = UserTour.objects.filter(applied_by=user)

        # Apply additional filters (status, date, etc.)
        selected_status = (
            form.cleaned_data.get("status", settings.PENDING)
            if form.is_valid()
            else settings.PENDING
        )
        from_date = form.cleaned_data.get("from_date")
        to_date = form.cleaned_data.get("to_date")

        if selected_status:
            user_tours = user_tours.filter(status=selected_status)
        if from_date:
            user_tours = user_tours.filter(start_date__gte=from_date)
        if to_date:
            user_tours = user_tours.filter(end_date__lte=to_date)

        # Get the tours assigned to the user's employees (if the user is an RM)
        if user.is_rm:
            employee_tours = UserTour.objects.filter(
                applied_by__in=user.employees.all()
            )
            from_date = form.cleaned_data.get("from_date")
            to_date = form.cleaned_data.get("to_date")
            if selected_status:
                employee_tours = employee_tours.filter(status=selected_status)
            if from_date:
                employee_tours = employee_tours.filter(start_date__gte=from_date)
            if to_date:
                employee_tours = employee_tours.filter(end_date__lte=to_date)
            context.update(
                {
                    "employee_tours": employee_tours,
                }
            )

        # Add the current date and URLs for navigation
        context.update(
            {
                "current_date": now(),
                "form": form,
                "search_term": self.request.GET.get("search", ""),
                "selected_status": selected_status,
                "urls": [
                    ("dashboard", {"label": "Dashboard"}),
                    ("tour_tracker", {"label": "Tour Tracker"}),
                ],
            }
        )

        return context


class ApplyTourView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = UserTour
    form_class = TourForm
    title = _("Apply Tour")
    template_name = "hrms_app/apply-tour.html"
    success_url = reverse_lazy("tour_tracker")
    permission_required = "hrms_app.add_usertour"

    def test_func(self):
        return self.request.user.has_perm(self.permission_required)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        urls = [
            ("dashboard", {"label": "Dashboard"}),
            ("tour_tracker", {"label": "Tour Tracker"}),
            (
                "apply_tour",
                {"label": "Tour Application"},
            ),
        ]
        context["urls"] = urls
        return context

    def form_valid(self, form):
        tour = form.save(commit=False)
        tour.applied_by = self.request.user
        tour.save()
        messages.success(self.request, "Tour Applied Successfully")
        return super().form_valid(form)

    def form_invalid(self, form):
        return self.render_to_response(self.get_context_data(form=form))


class TourApplicationDetailView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = UserTour
    template_name = "hrms_app/tour_application_detail.html"
    context_object_name = "tour_application"
    form_class = TourStatusUpdateForm
    slug_field = "slug"
    slug_url_kwarg = "slug"

    def dispatch(self, request, *args, **kwargs):
        # Check if the user is authenticated
        if not request.user.is_authenticated:
            return self.handle_no_permission()

        # Perform the permission check
        if not self.test_func():
            raise PermissionDenied(_("You do not have permission to access this page."))

        return super().dispatch(request, *args, **kwargs)

    def test_func(self):
        # Determine the required permission dynamically based on the HTTP method
        if self.request.method in ["GET"]:
            permission_required = (
                f"{self.model._meta.app_label}.view_{self.model._meta.model_name}"
            )
        elif self.request.method in ["POST", "PUT", "PATCH"]:
            permission_required = (
                f"{self.model._meta.app_label}.change_{self.model._meta.model_name}"
            )
        else:
            # Default to a custom permission, if needed
            permission_required = getattr(self, "permission_required", None)

        return self.request.user.has_perm(permission_required)

    def get_object(self, queryset=None):
        tour_application = super().get_object(queryset)
        user = self.request.user
        if (
            tour_application.applied_by == user
            or user.is_superuser
            or user.is_staff
            or user.personal_detail.designation.department.department == "admin"
            or tour_application.applied_by.reports_to == user
        ):
            return tour_application
        raise PermissionDenied(
            "Only Employee, Manager and Admin can view His/Her tour details."
        )

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        tour_application = self.get_object()
        kwargs["user"] = self.request.user
        kwargs["is_manager"] = (
            self.request.user == tour_application.applied_by.reports_to
        )
        return kwargs

    def form_valid(self, form):
        self.object = form.save()
        messages.success(
            self.request,
            f"Tour {form.cleaned_data.get('status')} Successfully",
        )
        TourStatusLog.create_log(
            tour=self.object,
            action_by=self.request.user,
            action=form.cleaned_data.get("status"),
            comments=form.cleaned_data.get("reason"),
        )
        return HttpResponseRedirect(
            reverse("tour_application_detail", kwargs={"slug": self.object.slug})
        )

    def form_invalid(self, form, msg=None):
        return self.render_to_response(self.get_context_data(form=form))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        tour_application = self.get_object()
        current_url = self.request.get_full_path()

        urls = [
            ("dashboard", {"label": "Dashboard"}),
            ("tour_tracker", {"label": "Tour Tracker"}),
            (
                "tour_application_detail",
                {"label": f"{tour_application.slug}", "slug": tour_application.slug},
            ),
        ]
        context["is_manager"] = (
            self.request.user == tour_application.applied_by.reports_to
        )
        # Add the 'next' parameter to the delete URL
        context["delete_url"] = reverse(
            "generic_delete",
            kwargs={"model_name": self.model.__name__, "pk": self.get_object().pk},
        )
        context["delete_url"] += "?" + urlencode({"next": current_url})

        # Add the 'next' parameter to the edit URL
        context["edit_url"] = reverse(
            "tour_application_update", kwargs={"slug": self.get_object().slug}
        )
        context["edit_url"] += "?" + urlencode({"next": current_url})

        context["pdf_url"] = reverse(
            "generate_tour_pdf", kwargs={"slug": self.get_object().slug}
        )
        context["urls"] = urls
        return context

    def get_success_url(self):
        return reverse_lazy(
            "tour_application_detail", kwargs={"slug": self.object.slug}
        )


class TourApplicationUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = UserTour
    form_class = TourForm
    template_name = "hrms_app/apply-tour.html"
    permission_required = "hrms_app.change_usertour"

    def test_func(self):
        return self.request.user.has_perm(self.permission_required)

    def get_object(self, queryset=None):
        return get_object_or_404(UserTour, slug=self.kwargs.get("slug"))

    def form_valid(self, form):
        response = super().form_valid(form)
        tour_application = form.instance
        reason = form.cleaned_data.get("reason")
        action_by = self.request.user
        if tour_application.status == settings.APPROVED:
            tour_application.approve(action_by=action_by, reason=reason)
        elif tour_application.status == settings.REJECTED:
            tour_application.reject(action_by=action_by, reason=reason)
        elif tour_application.status == settings.CANCELLED:
            tour_application.cancel(action_by=action_by, reason=reason)
        elif tour_application.status == settings.COMPLETED:
            tour_application.complete(action_by=action_by, reason=reason)
        elif tour_application.status == settings.EXTENDED:
            tour_application.extend(action_by=action_by, reason=reason)
        elif tour_application.status == settings.PENDING_CANCELLATION:
            TourStatusLog.create_log(
                tour=tour_application,
                action_by=action_by,
                action="Cancellation request",
                comments=reason,
            )
        else:
            TourStatusLog.create_log(
                tour=tour_application,
                action_by=action_by,
                action="Updated",
                comments=reason,
            )
        messages.success(self.request, "Tour status updated successfully.")
        return response

    def get_success_url(self):
        return reverse_lazy(
            "tour_application_detail", kwargs={"slug": self.object.slug}
        )


from django.http import HttpResponse
from weasyprint import HTML
from django.template.loader import render_to_string


class GenerateTourPDFView(View):
    def get(self, request, slug):
        tour_details = get_object_or_404(UserTour, slug=slug)
        logo = Logo.objects.all().first()
        context = {
            "object": tour_details,
            "logo": logo,
        }
        html_template = "pdf/tour_details_pdf.html"
        html_content = render_to_string(html_template, context, request=request)
        pdf_file = HTML(
            string=html_content, base_url=request.build_absolute_uri()
        ).write_pdf()
        response = HttpResponse(pdf_file, content_type="application/pdf")
        response["Content-Disposition"] = 'inline; filename="tour_details.pdf"'
        return response


class UploadBillView(LoginRequiredMixin, UserPassesTestMixin, FormView):
    form_class = BillForm
    template_name = "hrm_app/upload_bill.html"

    def get_success_url(self):
        return reverse_lazy("tour_detail", kwargs={"slug": self.kwargs["slug"]})

    def form_valid(self, form):
        tour = get_object_or_404(UserTour, pk=self.kwargs["pk"])
        bill = form.save(commit=False)
        bill.tour = tour
        bill.save()
        tour.bills_submitted = True
        tour.save()
        return super().form_valid(form)

    def test_func(self):
        tour = get_object_or_404(UserTour, pk=self.kwargs["pk"])
        return self.request.user == tour.applied_by


class CustomUploadView(View):
    @csrf_exempt
    def post(self, request, *args, **kwargs):
        file = request.FILES.get("upload")
        if file:
            file_name = default_storage.save(file.name, ContentFile(file.read()))
            file_url = default_storage.url(file_name)
            response = {
                "url": file_url,
                "uploaded": True,
                "message": "File uploaded successfully",
            }
        else:
            response = {"uploaded": False, "message": "No file uploaded"}
        return JsonResponse(response)


from formtools.wizard.views import SessionWizardView

FORMS = [
    ("user", CustomUserForm),
    ("personal", PersonalDetailsForm),
    ("paddress", PermanentAddressForm),
    ("caddress", CorrespondingAddressForm),
]

TEMPLATES = {
    "user": "hrms_app/wizard/user_form.html",
    "personal": "hrms_app/wizard/personal_details_form.html",
    "paddress": "hrms_app/wizard/paddress_form.html",
    "caddress": "hrms_app/wizard/caddress_form.html",
}


class UserCreationWizard(LoginRequiredMixin, SessionWizardView):
    file_storage = FileSystemStorage(location=settings.MEDIA_ROOT)
    template_name = "hrms_app/form_wizard.html"
    url_name = reverse_lazy("/")

    def get_template_names(self):
        return [TEMPLATES[self.steps.current]]

    def get_user_instance(self):
        user_id = self.kwargs.get("pk")
        return get_object_or_404(CustomUser, pk=user_id) if user_id else None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["urls"] = [
            ("dashboard", {"label": "Dashboard"}),
            ("create_user", {"label": "Create Employee"}),
        ]
        return context

    def get_form_initial(self, step):
        user = self.get_user_instance()
        if user:
            progress = FormProgress.objects.filter(user=user, step=step).first()
            if progress:
                return progress.data

            model_class = self.form_list[step]._meta.model
            instance = (
                model_class.objects.filter(user_id=user.pk).first()
                if model_class != CustomUser
                else model_class.objects.filter(pk=user.pk).first()
            )
            return model_to_dict(instance) if instance else None

        return super().get_form_initial(step)

    def done(self, form_list, **kwargs):
        try:
            with transaction.atomic():
                return self.save_forms(form_list)
        except Exception as e:
            logger.error(f"Error during form submission in done method: {e}")
            return self.render_error_page()

    def save_forms(self, form_list):
        user_form, personal_details_form, paddress_form, caddress_form = form_list
        user = self.get_user_instance()

        if not user:
            user = user_form.save(commit=False)
            user.set_password("12345@Kmpcl")  # Set a default password for new users
            user.save()
        else:
            user_form.save()

        personal_details = personal_details_form.save(commit=False)
        personal_details.user = user
        personal_details.save()

        paddress = paddress_form.save(commit=False)
        paddress.user = user
        paddress.save()

        caddress = caddress_form.save(commit=False)
        caddress.user = user
        caddress.save()

        FormProgress.objects.filter(user=user).update(status="completed")
        return redirect("employees")

    def post(self, *args, **kwargs):
        current_step = self.steps.current
        user = self.get_user_instance()

        if "wizard_goto_step" in self.request.POST:
            return self.render_goto_step(self.request.POST["wizard_goto_step"])

        form = self.get_form(
            current_step, data=self.request.POST, files=self.request.FILES
        )
        if form.is_valid():
            if user:
                self.save_form_data(user, current_step, form.cleaned_data)
            return super().post(*args, **kwargs)

        return self.render(form)

    def save_form_data(self, user, current_step, form_data):
        try:
            FormProgress.objects.update_or_create(
                user=user, step=current_step, defaults={"data": form_data}
            )
        except IntegrityError as e:
            logger.error(f"Error saving form data for step {current_step}: {e}")
            raise

    def render_error_page(self):
        return redirect("error_page")


def cancel_user_creation(request):
    request.session.pop("current_step", None)
    return redirect("/")


class EmployeeListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = CustomUser
    template_name = "hrms_app/employee/employees.html"
    context_object_name = "users"
    paginate_by = 20

    def test_func(self):
        # Allow access only to staff and superusers
        return self.request.user.is_staff or self.request.user.is_superuser

    def get_queryset(self):
        queryset = CustomUser.objects.all()

        # Filter by active status if provided in GET params
        is_active = self.request.GET.get("is_active")
        if is_active is not None and is_active != "":
            queryset = queryset.filter(is_active=is_active)

        # Search by username, first name, last name, or email
        search_query = self.request.GET.get("q")
        if search_query:
            queryset = queryset.filter(
                Q(username__icontains=search_query)
                | Q(first_name__icontains=search_query)
                | Q(last_name__icontains=search_query)
                | Q(email__icontains=search_query)
                | Q(official_email__icontains=search_query)
            )

        return queryset.order_by("-date_joined")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Pass search query and is_active filter to the context for form persistence
        context["search_query"] = self.request.GET.get("q", "")
        context["is_active"] = self.request.GET.get("is_active", "")
        urls = [
            ("dashboard", {"label": "Dashboard"}),
            ("employees", {"label": "Employee List"}),
        ]
        context["urls"] = urls
        return context


class LeaveTransactionCreateView(FormView):
    form_class = LeaveTransactionForm
    template_name = "hrms_app/leave_transaction.html"
    title = _("Leave Transaction")

    def get_success_url(self):
        # Redirect back to the same form for creating a new transaction
        return reverse_lazy("leave_transaction_create")

    def form_valid(self, form):
        try:
            # Process the form and create transactions
            form.process()
            messages.success(self.request, "Leave transaction applied successfully.")
        except ValueError as e:
            messages.error(self.request, f"Error: {e}")
            return self.form_invalid(form)  # Return form with errors if process fails
        return redirect(self.get_success_url())

    def form_invalid(self, form):
        # Add an error message and render the form again
        messages.error(
            self.request,
            "There was an error with your submission. Please check the form and try again.",
        )
        return super().form_invalid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        urls = [
            ("dashboard", {"label": "Dashboard"}),
            ("leave_transaction_create", {"label": "Leave Transaction"}),
        ]
        context.update({"urls": urls, "title": self.title})
        return context


class LeaveBalanceUpdateView(View):
    template_name = "hrms_app/leave_bal_up.html"

    def get(self, request, *args, **kwargs):
        form = LeaveBalanceForm()
        return render(request, self.template_name, {"form": form})

    def post(self, request, *args, **kwargs):
        form = LeaveBalanceForm(request.POST)
        if form.is_valid():
            user = form.cleaned_data.get("user")
            leave_type = form.cleaned_data["leave_type"]
            year = form.cleaned_data["year"]
            opening_balance = form.cleaned_data.get("opening_balance")
            closing_balance = form.cleaned_data.get("closing_balance")
            no_of_leaves = form.cleaned_data.get("no_of_leaves")
            remaining_leave_balances = form.cleaned_data.get("remaining_leave_balances")

            try:
                with transaction.atomic():
                    if user:
                        # Update only for the selected user
                        leave_balances = LeaveBalanceOpenings.objects.filter(
                            user=user, leave_type=leave_type, year=year
                        )
                    else:
                        # Update for all users with the selected leave type
                        leave_balances = LeaveBalanceOpenings.objects.filter(
                            leave_type=leave_type, year=year
                        )

                    if leave_balances.exists():
                        for balance in leave_balances:
                            if opening_balance is not None:
                                balance.opening_balance = opening_balance
                            if closing_balance is not None:
                                balance.closing_balance = closing_balance
                            if no_of_leaves is not None:
                                balance.no_of_leaves = no_of_leaves
                            if remaining_leave_balances is not None:
                                balance.remaining_leave_balances = (
                                    remaining_leave_balances
                                )
                            balance.save(
                                update_fields=[
                                    "opening_balance",
                                    "closing_balance",
                                    "no_of_leaves",
                                    "remaining_leave_balances",
                                ]
                            )

                        messages.success(
                            request, "Leave balances updated successfully."
                        )
                    else:
                        # If no leave balances exist, create them
                        messages.warning(request, "No existing leave balances found.")
                        if user:
                            LeaveBalanceOpenings.objects.create(
                                user=user,
                                leave_type=leave_type,
                                year=year,
                                opening_balance=opening_balance or 0,
                                closing_balance=closing_balance or 0,
                                no_of_leaves=no_of_leaves or 0,
                                remaining_leave_balances=remaining_leave_balances or 0,
                                created_by=request.user,
                            )
                        else:
                            for user in CustomUser.objects.all():
                                LeaveBalanceOpenings.objects.create(
                                    user=user,
                                    leave_type=leave_type,
                                    year=year,
                                    opening_balance=opening_balance or 0,
                                    closing_balance=closing_balance or 0,
                                    no_of_leaves=no_of_leaves or 0,
                                    remaining_leave_balances=remaining_leave_balances
                                    or 0,
                                    created_by=request.user,
                                )
                        messages.success(
                            request, "New leave balances created successfully."
                        )

            except Exception as e:
                messages.error(request, f"An error occurred: {e}")

            return redirect("leave_bal_up")

        return render(request, self.template_name, {"form": form})
