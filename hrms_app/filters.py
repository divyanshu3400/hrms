import django_filters
from django.contrib.auth import get_user_model
from .models import UserTour

class UserTourFilter(django_filters.FilterSet):
    # Define your filter fields here
    applied_by = django_filters.ModelChoiceFilter(queryset=get_user_model().objects.all())
    
    class Meta:
        model = UserTour
        fields = ['applied_by']


from django_filters import rest_framework as filters
from .models import Notification

class NotificationFilter(filters.FilterSet):
    """
    FilterSet for Notification model to filter by timestamp.
    """
    from_date = filters.IsoDateTimeFilter(field_name="timestamp", lookup_expr="gte")
    to_date = filters.IsoDateTimeFilter(field_name="timestamp", lookup_expr="lte")

    class Meta:
        model = Notification
        fields = ["from_date", "to_date"]
