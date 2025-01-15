from django.contrib import admin
from django.urls import path,include,re_path
from hrms_app.hrms.sites import site
from django.conf.urls.static import static
from hrms_app.views.views import *
# urls.py
# from hrms_app.wishes import birthday as hbd

from django.conf.urls import handler403

handler403 = custom_permission_denied


urlpatterns = [
    path('admin/doc/', include('django.contrib.admindocs.urls')),
    path('admin/', admin.site.urls),
    path('leaves/', LeaveApplicationListView.as_view(), name='leave-application-list'),
    path("save-column-preferences/", save_column_preferences, name="save_column_preferences"),
    path('', include(site.get_urls())),
    path("ckeditor5/", include('django_ckeditor_5.urls')),
    path('schedule/', include('schedule.urls')),
    path("upload/", CustomUploadView.as_view(), name="custom_upload_file"),
    path("events-list/", EventListView.as_view(), name="event_list"),
    path('create-user/', UserCreationWizard.as_view(FORMS), name='create_user'),
    path('create-user/<int:pk>/', UserCreationWizard.as_view(FORMS), name='edit_user_wizard'),
    path('cancel-user-creation/', cancel_user_creation, name='cancel_user_creation'),
    path("api/v1/", include('hrms_app.urls')),
    re_path(r'^webpush/', include('webpush.urls')),
    path('<str:title>/success/', TemplateView.as_view(template_name='hrms_app/generic_success.html'), name='success_page'),
    # path('hbd-index', hbd.index, name='index'),
    # path('wish/', hbd.wish, name='wish'),
    # path('stop_sound/', hbd.stop_sound, name='stop_sound'),
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)