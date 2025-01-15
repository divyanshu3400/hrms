# serializers.py
from rest_framework import serializers
from django.utils.translation import gettext_lazy as _
from hrms_app.models import *
from hrms_app.utility.leave_utils import LeavePolicyManager
from django.utils import timezone
from datetime import datetime
from django.db.models import Q
from rest_framework import serializers
from django.contrib.auth.models import Permission, Group

class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = '__all__'  # Or specify the fields you need: ['id', 'name']

class PermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permission
        fields = ['id', 'name', 'codename']

class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ['id', 'name']


class LeaveApplicationSerializer(serializers.ModelSerializer):
    days = serializers.SerializerMethodField()

    class Meta:
        model = LeaveApplication
        fields = ["id", "leaveType", "startDate", "endDate", "days", "status"]

    def get_days(self, obj):
        return obj.leave_detail.usedLeave if obj.leave_detail else 0


class AttendanceLogActionSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = AttendanceLogAction
        fields = "__all__"


class AttendanceLogSerializer(serializers.ModelSerializer):
    actions = AttendanceLogActionSerializer(many=True,read_only = True)
    appliedByName = serializers.StringRelatedField(source="applied_by", read_only=True)

    class Meta:
        model = AttendanceLog
        fields = [
            "id",
            'title',
            "applied_by",
            "appliedByName",
            "start_date",
            "end_date",
            "from_date",
            "to_date",
            "reg_duration",
            "status",
            "is_regularisation",
            "duration",
            "reg_status",
            "att_status",
            "att_status_short_code",
            "color_hex",
            "updated_by",
            "created_at",
            "reason",
            "is_submitted",
            "slug",
            "actions",
        ]
        read_only_fields = [
            'title',
            'att_status', 
            'att_status_short_code', 
            'applied_by', 
            'appliedByName', 
            'color_hex',
            'slug', 
            "updated_by",
            "created_at",
            'actions',
        ]
        
    def create(self, validated_data):
        """
        Override the create method to handle custom logic, such as setting the created_by field.
        """
        user = self.context['request'].user
        validated_data['applied_by'] = user
        return super(OfficeLocationSerializer, self).create(validated_data)

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        user = self.context['request'].user
        validated_data['updated_by'] = user
        instance.save()
        return instance

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['isManager'] = self.context.get('isManager', False)
        return representation

class GenderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Gender
        fields = ["id", "gender", "is_active"]


class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Designation
        fields = ["id", "department", "slug", "is_active"]


class DesignationSerializer(serializers.ModelSerializer):
    department = DepartmentSerializer(read_only=True)

    class Meta:
        model = Designation
        fields = ["id", "department", "slug", "designation", "is_active"]


class ReligionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Religion
        fields = ["id", "religion", "is_active"]


class MaritalStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = MaritalStatus
        fields = ["id", "marital_status", "is_active"]

class CurrentUserSerializer(serializers.ModelSerializer):
    reports_to = serializers.StringRelatedField()
    
    role = RoleSerializer()
    user_permissions = PermissionSerializer(many=True)
    groups = GroupSerializer(many=True)


    class Meta:
        model = CustomUser
        exclude = ('password',)


class PersonalDetailsSerializer(serializers.ModelSerializer):
    gender = GenderSerializer(read_only=True)
    designation = DesignationSerializer(read_only=True)
    religion = ReligionSerializer(read_only=True)
    marital_status = MaritalStatusSerializer(read_only=True)
    user = CurrentUserSerializer(read_only=True)

    class Meta:
        model = PersonalDetails
        fields = [
            "id",
            "employee_code",
            "user",
            "avatar",
            "mobile_number",
            "alt_mobile_number",
            "gender",
            "designation",
            "official_mobile_number",
            "religion",
            "marital_status",
            "birthday",
            "marriage_ann",
            "doj",
            "dol",
            "dor",
            "dof",
        ]


class ShiftSerializer(serializers.ModelSerializer):
    role = serializers.StringRelatedField(read_only=True)
    class Meta:
        model = ShiftTiming
        fields = [
            "id",
            "start_time",
            "end_time",
            "grace_time",
            "grace_start_time",
            "grace_end_time",
            "break_start_time",
            "break_end_time",
            "break_duration",
            "role",
            "is_active",
        ]


class EmployeeShiftSerializer(serializers.ModelSerializer):
    shift_timing = ShiftSerializer(read_only=True)
    class Meta:
        model = EmployeeShift
        fields = ["id", "employee", "shift_timing", "created_at", "created_by"]


# serializers.py


class LeaveLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = LeaveLog
        fields = [
            "id",
            "action_by_name",
            "action_by_email",
            "action",
            "timestamp",
            "notes",
        ]


class LeaveTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = LeaveType
        fields = [
            "id",
            "leave_type",
            "leave_type_short_code",
            "min_notice_days",
            "max_days_limit",
            "min_days_limit",
            "allowed_days_per_year",
            "leave_fy_start",
            "leave_fy_end",
            "color_hex",
            "text_color_hex",
        ]


class LeaveBalanceOpeningSerializer(serializers.ModelSerializer):
    leave_type = LeaveTypeSerializer()

    class Meta:
        model = LeaveBalanceOpenings
        fields = [
            "id",
            "no_of_leaves",
            "remaining_leave_balances",
            "leave_type",
            "year",
        ]


class AttendanceSettingSerializer(serializers.ModelSerializer):
    class Meta:
        model = AttendanceSetting
        fields = "__all__"


class AttendanceStatusColorSerializer(serializers.ModelSerializer):
    class Meta:
        model = AttendanceStatusColor
        fields = "__all__"

  
class HolidaySerializer(serializers.ModelSerializer):
    class Meta:
        model = Holiday
        fields = (
            "title",
            "short_code",
            "start_date",
            "end_date",
            "desc",
            "color_hex",
            "created_by",
        )


class NotificationSerializer(serializers.ModelSerializer):
    sender = serializers.StringRelatedField()
    receiver = serializers.StringRelatedField()
    class Meta:
        model = Notification
        fields = '__all__'  # You can specify the fields explicitly if needed



class OfficeLocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = OfficeLocation
        fields = '__all__'  # You can also specify fields explicitly if needed.

    def create(self, validated_data):
        """
        Override the create method to handle custom logic, such as setting the created_by field.
        """
        user = self.context['request'].user  # Get the user from the request context
        validated_data['created_by'] = user  # Set the created_by field to the current user
        return super(OfficeLocationSerializer, self).create(validated_data)

    def update(self, instance, validated_data):
        """
        Override the update method to handle custom logic, such as setting the updated_by field.
        """
        user = self.context['request'].user  # Get the user from the request context
        validated_data['updated_by'] = user  # Set the updated_by field to the current user
        return super(OfficeLocationSerializer, self).update(instance, validated_data)


class DeviceInformationSerializer(serializers.ModelSerializer):
    
    device_location = serializers.StringRelatedField(read_only=True)
    
    class Meta:
        model = DeviceInformation
        fields = '__all__'  
        
    def create(self, validated_data):
        """
        Override create method to handle additional logic if needed.
        For example, hashing the password before saving.
        """

        return super(DeviceInformationSerializer, self).create(validated_data)

    def update(self, instance, validated_data):
        """
        Override update method to handle additional logic if needed.
        For example, hashing the new password before updating.
        """

        return super(DeviceInformationSerializer, self).update(instance, validated_data)

class CustomUserSerializer(serializers.ModelSerializer):
    
    employees = serializers.StringRelatedField(many=True, read_only=True)
    device_location = OfficeLocationSerializer(read_only=True)

    class Meta:
        model = CustomUser
        fields = "__all__"


class TourLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = TourStatusLog
        fields = [
            "id",
            "action_by_name",
            "action_by_email",
            "action",
            "timestamp",
            "status",
            "comments",
        ]
        
class LeaveApplicationSerializer(serializers.ModelSerializer):
    leave_type_url = serializers.HyperlinkedRelatedField(
        view_name="leavetype-detail", read_only=True, source="leave_type"
    )
    logs = LeaveLogSerializer(many=True, read_only=True)
    
    # Use PrimaryKeyRelatedField for creation and LeaveTypeSerializer for retrieval
    leave_type = serializers.PrimaryKeyRelatedField(queryset=LeaveType.objects.all(), write_only=True)
    leave_type_detail = LeaveTypeSerializer(read_only=True, source="leave_type")
    appliedByName = serializers.StringRelatedField(source="appliedBy", read_only=True)
    avatar = serializers.SerializerMethodField()
    class Meta:
        model = LeaveApplication
        fields = [
            "id",
            "applicationNo",
            "avatar",
            "leave_type",
            "leave_type_detail",
            "leave_type_url",
            "startDate",
            "appliedBy",
            "appliedByName",
            "endDate",
            "usedLeave",
            "balanceLeave",
            "reason",
            "status",
            "startDayChoice",
            "endDayChoice",
            "updatedAt",
            "slug",
            "logs",
        ]
        read_only_fields = [
            'id', 
            'applicationNo', 
            'leave_type_url', 
            'appliedBy', 
            'appliedByName', 
            'leave_type_detail',
            'slug', 
            'createdAt', 
            'updatedAt', 
            'logs'
        ]
    def get_avatar(self, obj):
        # Navigate through the relationship to fetch the avatar
        personal_detail = getattr(obj.appliedBy, "personal_detail", None)
        if personal_detail and personal_detail.avatar:
            request = self.context.get("request")  # Use the request object for full URL
            if request:
                return request.build_absolute_uri(personal_detail.avatar.url)
            return personal_detail.avatar.url  # Return relative URL if request is not available
        return None  # Return None if no avatar exists
    
    def validate(self, data):
        """Validate leave application data."""
        request_method = self.context['request'].method

        # Check for missing fields on POST (creation)
        if request_method == 'POST':
            start_date = data.get("startDate")
            end_date = data.get("endDate")
            leave_type = data.get("leave_type")

            if not leave_type:
                raise serializers.ValidationError({
                    'non_field_errors': [_("Leave type is required.")]
                })

            if not start_date or not end_date:
                raise serializers.ValidationError({
                    'non_field_errors': [_("Both start date and end date are required.")]
                })

            if start_date > end_date:
                raise serializers.ValidationError({
                    'non_field_errors': [_("Start date cannot be after end date.")]
                })

            user = self.context["request"].user

            # Leave policy validation
            try:
                policy_manager = LeavePolicyManager(
                    user=user,
                    leave_type=leave_type,
                    start_date=start_date,
                    end_date=end_date,
                    start_day_choice=data.get("startDayChoice"),
                    end_day_choice=data.get("endDayChoice")
                )
                policy_manager.validate_policies()
            except serializers.ValidationError as e:
                raise serializers.ValidationError({
                    'non_field_errors': [str(e)]
                })

        return data

    def create(self, validated_data):
        """Create a new leave application."""
        user = self.context['request'].user
        leave_application = LeaveApplication.objects.create(
            appliedBy=user,
            applyingDate=timezone.now(),
            **validated_data
        )
        return leave_application

    def update(self, instance, validated_data):
        """Update an existing leave application."""
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['isManager'] = self.context.get('isManager', False)
        if self.context['request'].method in ['GET']:
            leave_type_serializer = LeaveTypeSerializer(instance.leave_type)
            representation['leave_type'] = leave_type_serializer.data
        return representation


class UserTourSerializer(serializers.ModelSerializer):
    logs = TourLogSerializer(many=True, read_only=True)
    appliedByName = serializers.StringRelatedField(source="applied_by", read_only=True)
    avatar = serializers.SerializerMethodField()
    class Meta:
        model = UserTour
        fields = [
            'id','avatar', 'applied_by', 'appliedByName', 'from_destination', 'to_destination',
            'start_date', 'start_time', 'end_date', 'end_time', 'updated_at',
            'created_at', 'remarks', 'status', 'extended_end_date', 'extended_end_time',
            'bills_submitted', 'slug', 'approval_type', 'logs'
        ]
        read_only_fields = ['id', 'slug', 'created_at', 'updated_at', 'logs', 'applied_by']

    def get_avatar(self, obj):
        # Navigate through the relationship to fetch the avatar
        personal_detail = getattr(obj.applied_by, "personal_detail", None)
        if personal_detail and personal_detail.avatar:
            request = self.context.get("request")  # Use the request object for full URL
            if request:
                return request.build_absolute_uri(personal_detail.avatar.url)
            return personal_detail.avatar.url  # Return relative URL if request is not available
        return None  # Return None if no avatar exists
    
    def validate(self, attrs):
        approval_type = attrs.get('approval_type')
        start_date_str = attrs.get('start_date')
        end_date_str = attrs.get('end_date')
        current_date = timezone.now().date()
        request = self.context.get('request')
        user = request.user

        # Convert date strings to date objects if needed
        if isinstance(start_date_str, str):
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
        else:
            start_date = start_date_str

        if isinstance(end_date_str, str):
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
        else:
            end_date = end_date_str

        # Check for overlapping tours
        overlapping_tours = UserTour.objects.filter(
            Q(start_date__lte=end_date) & Q(end_date__gte=start_date),
            applied_by=user,
            status__in=[settings.PENDING,settings.PENDING_CANCELLATION, settings.APPROVED]
        ).exclude(id=self.instance.id if self.instance else None)

        if overlapping_tours.exists():
            raise serializers.ValidationError(_("You already have an approved or pending tour within the selected date range."))

        # PRE_APPROVAL specific checks
        if approval_type == settings.PRE_APPROVAL:
            if start_date < current_date:
                raise serializers.ValidationError(_("Start date must be today or in the future for PRE_APPROVAL."))
            if end_date < start_date:
                raise serializers.ValidationError(_("End date must be greater than start date for PRE_APPROVAL."))

        # POST_APPROVAL specific checks
        elif approval_type == settings.POST_APPROVAL:
            if start_date >= current_date:
                raise serializers.ValidationError(_("Start date must be in the past for POST_APPROVAL."))
            if end_date <= start_date:
                raise serializers.ValidationError(_("End date must be greater than start date for POST_APPROVAL."))

        return attrs

    def validate_start_date(self, value):
        if value < timezone.now().date():
            raise serializers.ValidationError(_("Start date cannot be in the past."))
        return value

    def validate_end_date(self, value):
        # Convert start_date to datetime.date if it's a string
        start_date_str = self.initial_data.get('start_date')
        if isinstance(start_date_str, str):
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
        else:
            start_date = start_date_str

        if start_date and value < start_date:
            raise serializers.ValidationError(_("End date must be greater than start date."))
        return value

    def create(self, validated_data):
        """Create a new leave application."""
        request = self.context.get("request")
        user = request.user
        
        # Remove 'applied_by' from validated_data, as we set it directly
        validated_data.pop('applied_by', None)  # This ensures applied_by is not expected in the input

        user_tour = UserTour.objects.create(
            applied_by=user, **validated_data
        )
        return user_tour

    def update(self, instance, validated_data):
        """Update an existing tour application."""
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['isManager'] = self.context.get('isManager', False)
        return representation

class LogASerializer(serializers.ModelSerializer):
    class Meta:
        model = AttendanceLog
        fields = ['applied_by', 'start_date', 'end_date','duration']
        pandas_index = ['start_date']
        pandas_scatter_coord = ['duration']
        pandas_scatter_header = ['applied_by']
