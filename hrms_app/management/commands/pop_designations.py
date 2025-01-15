from django.core.management.base import BaseCommand
from hrms_app.models import Role, Gender, Designation, Department
from django.db.utils import IntegrityError
from django.utils.text import slugify

class Command(BaseCommand):
    help = 'Populate UserType data'

    def handle(self, *args, **options):
        designations = [
            'Assistant Manager-F&A',
            'Assistant Manager-F&A',
            'Assistant Manager-PES',
            'Assistant Manager-PIB',
            'Assistant Manager-Purchase',
            'Assistant Manager-Quality',
            'Assistant Manager-Sales',
            'Assistant Store Keeper',
            'Asst- PES',
            'Chemist',
            'Facilitator',
            'Chief Executive',
            'Dy. Manager - Quality',
            'Executive - MCC Incharge (Trainee)',
            'Executive- MCC Incharge',
            'Executive-BMC Incharge',
            'Executive- Logistics',
            'Executive- Logistics (Trainee)',
            'Executive- Sales',
            'Executive-Area Operation',
            'Executive-ERP (IT)',
            'Executive-F&A',
            'Executive-FES',
            'Executive-HR',
            'Executive-HR (Trainee)',
            'Executive-IT',
            'Executive-MIS',
            'Sr. Executive-P.I.B',
            'Executive-P.I.B',
            'Executive-PES',
            'Executive-Quality',
            'Executive-Store Incharge',
            'Head - Field Operations',
            'Head-Cluster Operations',
            'Manager- Finance & Accounts',
            'Manager- HR',
            'Manager-Cluster Operations',
            'Manager-CS & Legal',
            'Manager-Field Operations',
            'Manager-IT & MIS',
            'Manager-Legal & CS',
            'Manager-Quality ',
        ]
        
        department = Department.objects.first()  # Assuming at least one department exists
        
        for designation in designations:
            # Generate a slug from the designation
            slug = slugify(designation)
            
            # Check if a designation with the same slug already exists
            if not Designation.objects.filter(department=department, slug=slug).exists():
                try:
                    # Create the designation if it doesn't already exist
                    Designation.objects.create(department=department, designation=designation, slug=slug)
                except IntegrityError:
                    self.stderr.write(f"IntegrityError occurred for designation: {designation}")
            else:
                self.stdout.write(f"Designation '{designation}' already exists, skipping.")
        
        self.stdout.write(self.style.SUCCESS('Data populated successfully'))
