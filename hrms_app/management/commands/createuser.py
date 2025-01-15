from django.core.management.base import BaseCommand
from django.utils.translation import gettext as _
from hrms_app.models import CustomUser
class Command(BaseCommand):
    help = 'Creates a superuser with custom role'

    def add_arguments(self, parser):
        parser.add_argument('--role', type=str, help='Specify the role for the user')

    def handle(self, *args, **kwargs):
        username = input('Enter username: ')
        email = input('Enter email address: ')
        password = input('Enter password: ')
        role = kwargs.get('role')

        if not role:
            role = 'admin'
        try:
            user = CustomUser.objects.create_superuser(username=username, email=email, password=password)
            user.role = role
            user.save()
            self.stdout.write(self.style.SUCCESS(_(f'User {role} created successfully.')))
        except Exception as e:
            self.stderr.write(self.style.ERROR(_('Error creating superuser: %s' % e)))
