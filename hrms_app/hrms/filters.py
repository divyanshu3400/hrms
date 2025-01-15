import django_filters
from hrms_app.models import AttendanceLog
from django.db.models import Q
from django.contrib.auth import get_user_model

User = get_user_model()


class AttendanceLogFilter(django_filters.FilterSet):

    class Meta:
        model = AttendanceLog
        fields = {
            'status': ['exact'],
            'reg_status': ['exact'],
            'applied_by': ['exact'],
            'is_regularisation': ['exact'],
            'is_submitted': ['exact']
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        if not (user and (user.is_superuser or user.is_staff)):
            self.filters.pop('is_regularisation', None)
            # self.filters.pop('is_submitted', None)
        if user:
            if user.is_superuser or user.is_staff:
                self.filters['applied_by'].queryset = User.objects.all()
            elif hasattr(user, 'employees'):
                self.filters['applied_by'].queryset = User.objects.filter(
                    Q(id=user.id) | Q(id__in=user.employees.all())
                )
            else:
                self.filters['applied_by'].queryset = User.objects.filter(id=user.id)
