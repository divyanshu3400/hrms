from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from hrms_app.hrms.form import *
from hrms_app.hrms.resources import  CustomUserResource,HolidayResource,UserTourResource,LeaveTransactionResource
from .models import *
from django_ckeditor_5.widgets import CKEditor5Widget
from django.utils.safestring import mark_safe
from import_export.admin import ImportExportModelAdmin

admin.site.site_title = "HRMS"
admin.site.site_header = "HRMS Administration"

class CustomUserAdmin(UserAdmin, ImportExportModelAdmin):
    resource_class = CustomUserResource
    model = CustomUser
    list_display = ['username', 'first_name', 'last_name', 'official_email', 'is_superuser', 
                    'is_staff', 'is_active', 'date_joined', 'last_login']
    fieldsets = UserAdmin.fieldsets + (
        ('Custom Fields', {'fields': ('official_email', 'is_rm', 'reports_to', 'role', 'device_location')}),
    )

admin.site.register(CustomUser, CustomUserAdmin)


class LeaveTypeAdmin(admin.ModelAdmin):
    form = LeaveTypeForm
    list_display = ['leave_type', 'leave_type_short_code','half_day_short_code', 'min_notice_days'
        , 'max_days_limit', 'min_days_limit', 'allowed_days_per_year', 'leave_fy_start', 'leave_fy_end',
                    'created_at', 'created_by', 'updated_at',
                    'updated_by','consecutive_restriction']
    
    fields = ('leave_type', 'leave_type_short_code','half_day_short_code', 'min_notice_days'
        ,'max_days_limit', 'min_days_limit', 'allowed_days_per_year', 'leave_fy_start', 'leave_fy_end','consecutive_restriction','restricted_after_leave_types')

    
    search_fields = ['leave_type']
    
    filter_horizontal = ['restricted_after_leave_types']

    def color_representation(self, obj):
        return mark_safe(f'<div style="width: 30px; height: 20px; background-color: {obj.color_hex}"></div>')

    color_representation.short_description = 'Color'

    def save_model(self, request, obj, form, change):
        obj._current_user = request.user
        super().save_model(request, obj, form, change)

    def text_color_representation(self, obj):
        return mark_safe(f'<div style="width: 30px; height: 20px; background-color: {obj.text_color_hex}"></div>')

    text_color_representation.short_description = 'Text Color'


admin.site.register(LeaveType, LeaveTypeAdmin)

class HolidayAdmin(ImportExportModelAdmin):
    resource_class = HolidayResource
    form = HolidayForm
    list_display = ['title', 'short_code', 'start_date', 'end_date', 'desc', 'color_representation']

    def color_representation(self, obj):
        return mark_safe(f'<div style="width: 30px; height: 20px; background-color: {obj.color_hex}"></div>')

    color_representation.short_description = 'Color'

admin.site.register(Holiday, HolidayAdmin)

class AttendanceStatusColorAdmin(admin.ModelAdmin):
    form = AttendanceStatusColorForm

    list_display = ['status', 'color', 'color_representation', 'created_at']

    def color_representation(self, obj):
        return mark_safe(f'<div style="width: 30px; height: 20px; background-color: {obj.color_hex}"></div>')

    color_representation.short_description = 'Color'


admin.site.register(AttendanceStatusColor, AttendanceStatusColorAdmin)


class AttendanceSettingAdmin(admin.ModelAdmin):
    list_display = ['full_day_hours', 'half_day_hours', 'created_at', 'updated_at']


admin.site.register(AttendanceSetting, AttendanceSettingAdmin)


class AttendanceLogAdmin(admin.ModelAdmin):
    list_display = (
        'applied_by', 'start_date', 'end_date', 'att_status', 'duration', 'color_representation', 'is_regularisation',
        'is_submitted','slug')
    search_fields = ['applied_by__first_name','applied_by__username', 'applied_by__last_name']
    list_filter = ['start_date', 'end_date',]

    def color_representation(self, obj):
        return mark_safe(f'<div style="width: 30px; height: 20px; background-color: {obj.color_hex}"></div>')

    color_representation.short_description = 'Status Color'


admin.site.register(AttendanceLog, AttendanceLogAdmin)


class AttendanceLogActionAdmin(admin.ModelAdmin):
    list_display = ('log', 'action_by', 'action_by_name', 'action_by_email', 'action', 'timestamp', 'notes')
    search_fields = ['action_by__first_name', 'action_by__last_name', 'action_by_email']


admin.site.register(AttendanceLogAction, AttendanceLogActionAdmin)

class UserTourAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    resource_class = UserTourResource
    list_display = ('approval_type', 'applied_by', 'from_destination', 'to_destination', 'start_date','start_time', 'end_date','end_time','extended_end_date','extended_end_time', 'status', 'total','bills_submitted')
    search_fields = ['applied_by__username', 'applied_by__first_name', 'applied_by__last_name']
    list_filter = ['start_date','approval_type']
    formfield_overrides = {
        models.TextField: {'widget': CKEditor5Widget()},
    }

admin.site.register(UserTour, UserTourAdmin)

from django.contrib import messages

@admin.register(AttendanceLogHistory)
class AttendanceLogHistoryAdmin(admin.ModelAdmin):
    actions = ['revert_to_this_state']
    list_display = ('attendance_log', 'modified_by', 'modified_at')
    search_fields = ('attendance_log__id', 'modified_by__username')
    list_filter = ('modified_at', 'modified_by')
    readonly_fields = ('modified_at',)

    def revert_to_this_state(self, request, queryset):
        for history in queryset:
            history.revert()
            messages.success(request, f"Reverted attendance log {history.attendance_log} to the state from {history.modified_at}.")

    revert_to_this_state.short_description = "Revert selected attendance logs to this state"


class LeaveBalanceOpeningAdmin(admin.ModelAdmin):
    list_display = (
        'user', 'leave_type', 'year', 'no_of_leaves', 'remaining_leave_balances', 'opening_balance','closing_balance','created_at', 'created_by',
        'updated_at',
        'updated_by')
    search_fields = ['user__username','user__first_name', 'user__last_name']
    list_filter = ('year','leave_type')
    readonly_fields = ('created_at', 'updated_at', 'created_by', 'updated_by')


admin.site.register(LeaveBalanceOpenings, LeaveBalanceOpeningAdmin)


class ReligionAdmin(admin.ModelAdmin):
    list_display = ('religion', 'is_active', 'created_at')  # Display these fields in the list view
    search_fields = ('religion',)  # Make 'religion' field searchable
    list_filter = ('is_active',)  # Add filter by 'is_active' field
    ordering = ('created_at',)  # Order the records by 'created_at'

# Register the model with the custom admin
admin.site.register(Religion, ReligionAdmin)


class LockStatusAdmin(admin.ModelAdmin):
    list_display = ('is_locked','from_date','to_date', 'locked_at')
    actions = ['toggle_lock']
    
    def toggle_lock(self, request, queryset):
        for lock in queryset:
            lock.is_locked = 'locked' if lock.is_locked == 'unlocked' else 'unlocked'
            lock.save()
            action = 'locked' if lock.is_locked == 'locked' else 'unlocked'
            self.message_user(request, f"System has been {action}.")
    toggle_lock.short_description = "Toggle Lock Status"
    
admin.site.register(LockStatus, LockStatusAdmin)


@admin.register(LeaveTransaction)
class LeaveTransactionAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    list_display = (
        'leave_balance', 
        'leave_type', 
        'transaction_date', 
        'no_of_days_applied', 
        'no_of_days_approved', 
        'transaction_type', 
        'remarks',
    )
    list_filter = (
        'transaction_type', 
        'transaction_date', 
        'leave_type',
    )
    search_fields = (
        'leave_balance__user__username',
        'leave_balance__user__first_name',
        'leave_balance__user__last_name',
        'leave_type__leave_type',
        'remarks',
    )
    date_hierarchy = 'transaction_date'
    resource_class = LeaveTransactionResource

@admin.register(LeaveStatusPermission)
class LeaveStatusPermissionAdmin(admin.ModelAdmin):
    list_display = ("role", "user", "status")  # Fields to display in the admin list view
    list_filter = ("role", "status")  # Filters for the list view
    search_fields = ("role", "user__username", "status")  # Search functionality
    # autocomplete_fields = ("user",)

class PersonalDetailAdmin(admin.ModelAdmin):
    list_display = (
        'employee_code',
        'user',
        'avatar',
        'mobile_number',
        'alt_mobile_number',
        'gender',
        'designation',
        'official_mobile_number',
        'religion',
        'marital_status',
        'birthday',
        'doj',
        'dol',
    )

    # Add filters
    list_filter = (
        'gender',
        'religion',
        'marital_status',
        'doj',
        'dol',
    )

    # Add search fields
    search_fields = [
        'user__first_name',
        'user__last_name',
        'employee_code',
        'mobile_number',
        'official_mobile_number',
    ]

    # Organize fields into fieldsets
    fieldsets = (
        ('Personal Information', {
            'fields': (
                'salutation', 
                'employee_code', 
                'user', 
                'avatar', 
                'gender', 
                'religion', 
                'marital_status', 
                'birthday'
            ),
        }),
        ('Contact Details', {
            'fields': (
                'mobile_number', 
                'alt_mobile_number', 
                'official_mobile_number',
            ),
        }),
        ('Job Details', {
            'fields': (
                'designation', 
                'marriage_ann',
                'doj', 
                'dor',
                'dot',
                'dof',
                'dol',
            ),
        }),
    )


admin.site.register(PersonalDetails, PersonalDetailAdmin)


class EmployeeShiftAdmin(admin.ModelAdmin):
    list_display = ['employee', 'shift_timing', 'created_at', 'created_by']
    search_fields = ['employee__first_name', 'employee__last_name']


admin.site.register(EmployeeShift, EmployeeShiftAdmin)


class LeaveApplicationAdmin(admin.ModelAdmin):
    list_display = ['appliedBy', 'leave_type', 'applicationNo', 'applyingDate'
        , 'startDate', 'endDate', 'usedLeave', 'balanceLeave', 'status'
        , 'startDayChoice', 'endDayChoice', 'updatedAt']
    list_filter = ("startDate","status","leave_type")
    search_fields = ['leave_type__leave_type', 'appliedBy__first_name', 'appliedBy__last_name']


admin.site.register(LeaveApplication, LeaveApplicationAdmin)


class FormProgressAdmin(admin.ModelAdmin):
    list_display = ['user', 'step', 'status']

    search_fields = ['user__first_name', 'user__last_name', 'email']


admin.site.register(FormProgress, FormProgressAdmin)


class DeviceInformationAdmin(admin.ModelAdmin):
    list_display = ['device_location','from_date', 'to_date', 'serial_number','username','password']
    fields = ('device_location','api_link','from_date', 'to_date', 'serial_number','username','password')
    search_fields = ['serial_number', 'username']
    

admin.site.register(DeviceInformation, DeviceInformationAdmin)


class OfficeLocationAdmin(admin.ModelAdmin):
    list_display = ['location_name','office_type', 'address', 'latitude','longitude']
    fields = ('location_name','office_type', 'address', 'latitude','longitude')
    search_fields = ['location_name']
    filter = ['office_type']
    

admin.site.register(OfficeLocation, OfficeLocationAdmin)

class ShiftTimingAdmin(admin.ModelAdmin):
    list_display = ['start_time','end_time', 'grace_time', 'grace_start_time','grace_end_time','break_start_time','break_end_time','break_duration','is_active','role']
    fields = ['start_time','end_time', 'grace_time', 'grace_start_time','grace_end_time','break_start_time','break_end_time','break_duration','is_active','role']
    

admin.site.register(ShiftTiming, ShiftTimingAdmin)


class RoleAdmin(admin.ModelAdmin):
    list_display = ['name','description']    

admin.site.register(Role, RoleAdmin)



class NotificationAdmin(admin.ModelAdmin):
    list_display = ('sender', 'receiver', 'notification_type', 'is_read', 'timestamp')  # Fields to display in the list view
    list_filter = ('notification_type', 'is_read', 'timestamp')  # Fields to filter by
    search_fields = ('message',)  # Fields to search by
    ordering = ('-timestamp',)  # Default ordering

    fieldsets = (
        (None, {
            'fields': ('sender', 'receiver', 'message', 'notification_type', 'target_url', 'go_route_mobile', 'is_read')
        }),
        ('Related Object Info', {
            'fields': ('related_object_id', 'related_content_type')
        }),
        ('Timestamp', {
            'fields': ('timestamp',),
            'classes': ('collapse',),  # Optional: Collapse this section by default
        }),
    )

admin.site.register(Notification, NotificationAdmin)


@admin.register(LeaveDayChoiceAdjustment)
class LeaveDayChoiceAdjustmentAdmin(admin.ModelAdmin):
    list_display = ('start_day_choice', 'end_day_choice', 'adjustment_value')
    list_filter = ('start_day_choice', 'end_day_choice')
    search_fields = ('start_day_choice', 'end_day_choice')



@admin.register(Logo)
class LogoAdmin(admin.ModelAdmin):
    list_display = ('logo', 'logo_image')
    search_fields = ('logo',)

@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('department', 'is_active', 'created_at', 'updated_at')
    search_fields = ('department',)
    list_filter = ('is_active',)
    readonly_fields = ('created_at', 'updated_at', 'created_by', 'updated_by')
    prepopulated_fields = {'slug': ('department',)}

@admin.register(Designation)
class DesignationAdmin(admin.ModelAdmin):
    list_display = ('designation', 'department', 'is_active', 'created_at', 'updated_at')
    search_fields = ('designation', 'department__department')
    list_filter = ('is_active', 'department')
    list_editable = ('department',)  # Fields to be editable in the list view
    prepopulated_fields = {'slug': ('designation',)}
    readonly_fields = ('created_at', 'updated_at', 'created_by', 'updated_by')

    # Add bulk action to save selected entries
    actions = ['bulk_save']

    def bulk_save(self, request, queryset):
        updated_count = 0
        for obj in queryset:
            # Perform any logic you need for bulk updates here (if needed)
            obj.save()  # Save each object
            updated_count += 1

        self.message_user(request, f'{updated_count} Designations were successfully saved.')

    bulk_save.short_description = "Save selected designations"

@admin.register(Gender)
class GenderAdmin(admin.ModelAdmin):
    list_display = ('gender', 'is_active', 'created_at')
    search_fields = ('gender',)
    list_filter = ('is_active',)
    readonly_fields = ('created_at', 'updated_by', 'created_by')

@admin.register(MaritalStatus)
class MaritalStatusAdmin(admin.ModelAdmin):
    list_display = ('marital_status', 'is_active', 'created_at')
    search_fields = ('marital_status',)
    list_filter = ('is_active',)
    readonly_fields = ('created_at',)

@admin.register(LeaveDay)
class LeaveDayAdmin(admin.ModelAdmin):
    list_display = ("leave_application", "date", "is_full_day")
    list_filter = ("is_full_day", "date")
    search_fields = ("leave_application__applicationNo", "leave_application__appliedBy__username")
    date_hierarchy = "date"
    ordering = ("-date",)

@admin.register(WishingCard)
class WishingCardAdmin(admin.ModelAdmin):
    list_display = ('type', 'created_at', 'image')  # Fields displayed in the admin list view
    list_filter = ('type', 'created_at')  # Add filters for type and creation date
    search_fields = ('type',)  # Enable search by type
    date_hierarchy = 'created_at'  # Date hierarchy for navigation by creation date
    ordering = ('-created_at',)  # Default ordering by creation date (descending)
