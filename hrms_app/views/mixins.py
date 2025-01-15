class LeaveListViewMixin:
    @staticmethod
    def get_headers():
        return [
            {
                "name": "id",
                "title": "ID",
                "size": 50,
                "sortable": True,
                "sortDir": "asc",
            },
            {
                "name": "applied_by",
                "title": "Applied by",
                "size": 50,
                "sortable": True,
                "sortDir": "asc",
            },
            {
                "name": "from_place",
                "title": "Boarding",
                "sortable": True,
                "sortDir": "asc",
            },
            {
                "name": "start_date",
                "title": "Start Date",
                "sortable": True,
                "size": 150,
                "format": "date",
                "sortDir": "asc",
                "formatMask": "dd-mm-yyyy"
            },
            {
                "name": "to_place",
                "title": "Destination",
                "sortable": True,
                "sortDir": "asc",
                "size": 150,
            },
            {
                "name": "end_date",
                "title": "End Date",
                "sortable": True,
                "size": 150,
                "sortDir": "asc",
                "format": "date",
                "formatMask": "dd-mm-yyyy"
            },
            {
                "name": "end_type",
                "title": "End Type",
                "sortable": True,
                "sortDir": "asc",
                "size": 150,
            },
            {
                "name": "days",
                "title": "Days",
                "sortable": True,
                "sortDir": "asc",
                "size": 80
            },
            {
                "name": "status",
                "title": "Status",
                "sortable": True,
                "size": 150,
                "sortDir": "asc",
                "show": True
            }
        ]


from django.core.exceptions import PermissionDenied

class ModelPermissionRequiredMixin:
    model = None
    permission_action = "view"

    def has_permission(self, user):
        if not self.model:
            raise ValueError("The 'model' attribute must be set.")
        opts = self.model._meta
        perm = f"{opts.app_label}.{self.permission_action}_{opts.model_name}"
        return user.has_perm(perm)

    def dispatch(self, request, *args, **kwargs):
        if not self.has_permission(request.user):
            raise PermissionDenied("You do not have the required permissions.")
        return super().dispatch(request, *args, **kwargs)
