from .models import *
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.urls import reverse
from celery import shared_task
from django.core.mail import EmailMessage
from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.core.mail import EmailMultiAlternatives
import base64
from decouple import config
import os
import subprocess
import logging
from django.utils.timezone import now, localtime
from decouple import config
from webpush import send_user_notification

DEBUG = config('DEBUG', default=False, cast=bool)
USER = get_user_model()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),  # Output to console
        # Uncomment the following line to log to a file:
        # logging.FileHandler('api_logs.log')  # Output to a file
    ]
)


@shared_task
def send_leave_application_notifications(application_id, protocol, domain):
    leave_application = LeaveApplication.objects.get(id=application_id)
    user = leave_application.appliedBy
    manager = user.reports_to

    def create_email_context(title, content, leave_application, protocol, domain):
        return {
            "title": title,
            "content": content,
            "detail_url": f"{protocol}://{domain}{reverse('leave_application_detail', kwargs={'slug': leave_application.slug})}",
        }

    def send_email(subject, content, recipient):
        context = create_email_context(
            subject, content, leave_application, protocol, domain
        )
        message = render_to_string("email/leave_application_email.txt", context)
        send_leave_application_email.delay(subject, message, [recipient])

    # Employee email content
    employee_content = (
        f"Dear {user.first_name},\n\n"
        f"Your leave application ({leave_application.applicationNo}) has been {leave_application.status}.\n\n"
        f"Leave Details:\n"
        f"- Start Date: {localtime(leave_application.startDate).date()}\n"
        f"- End Date: {localtime(leave_application.endDate).date()}\n"
        f"- Leave Type: {leave_application.leave_type.leave_type}\n"
        f"Thank you,\n"
        f"Your HR Team"
    )
    employee_email = user.official_email if user.official_email else user.email
    send_email("Leave Application Status", employee_content, employee_email)

    # Manager email content
    manager_content = (
        f"Dear {manager.first_name} {manager.last_name},\n\n"
        f"A leave application ({leave_application.applicationNo}) by {user.get_full_name()} has been {leave_application.status}.\n\n"
        f"Leave Details:\n"
        f"- Start Date: {localtime(leave_application.startDate).date()}\n"
        f"- End Date: {localtime(leave_application.startDate).date()}\n"
        f"- Leave Type: {leave_application.leave_type.leave_type}\n"
        f"You can review the application at the following link:"
    )
    send_email(
        "Leave Application Status",
        manager_content,
        manager.official_email if manager.official_email else manager.email,
    )


@shared_task
def send_leave_application_email(subject, message, recipient_list):
    # print(f"Mail sent")

    if not DEBUG:
        send_mail(subject, message, settings.HRMS_DEFAULT_FROM_EMAIL, recipient_list)


def push_notification(user,head,body,url):
    payload = {"head": head, "body": body, 
        "icon": "http://hr.kasheemilk.com:7777/static/hrms_app/img/logo.png", "url": url}
    send_user_notification(user=user, payload=payload, ttl=1000)



@shared_task
def send_tour_notifications(tour_id, protocol, domain):
    user_tour = UserTour.objects.get(id=tour_id)
    user = user_tour.applied_by
    manager = user.reports_to

    def create_email_context(title, content, user_tour, protocol, domain):
        return {
            "title": title,
            "content": content,
            "detail_url": f"{protocol}://{domain}{reverse('tour_application_detail', kwargs={'slug': user_tour.slug})}",
        }

    def send_email(subject, content, recipient):
        context = create_email_context(subject, content, user_tour, protocol, domain)
        message = render_to_string("email/leave_application_email.txt", context)
        send_tour_application_email.delay(subject, message, [recipient])

    # Employee email content
    employee_content = (
        f"Dear {user.first_name},\n\n"
        f"Your tour application from ({user_tour.from_destination}) to ({user_tour.to_destination})  has been {user_tour.status}.\n\n"
        f"Tour Details:\n"
        f"- Boarding : {user_tour.from_destination} ({user_tour.start_date} {user_tour.start_time})\n"
        f"- Destination:  {user_tour.to_destination} ({user_tour.end_date} {user_tour.end_time})\n"
        f"- Status: {user_tour.status}\n"
        f"Thank you,\n"
        f"Your HR Team\n\n"
        f"You can review the tour detail at the following link:"
    )
    employee_email = user.official_email if user.official_email else user.email
    send_email("Tour Application Status", employee_content, employee_email)

    # Manager email content
    manager_content = (
        f"Dear {manager.first_name} {manager.last_name},\n\n"
        f"A Tour application requested by {user.get_full_name()} from ({user_tour.from_destination}) to ({user_tour.to_destination})  has been {user_tour.status}.\n\n"
        f"Tour Details:\n"
        f"- Boarding : {user_tour.from_destination} ({user_tour.start_date} {user_tour.start_time})\n"
        f"- Destination:  {user_tour.to_destination} ({user_tour.end_date} {user_tour.end_time})\n"
        f"- Status: {user_tour.status}\n"
        f"You can review the tour detail at the following link:"
    )
    send_email(
        "Tour Application Status",
        manager_content,
        manager.official_email if manager.official_email else manager.email,
    )


@shared_task
def send_tour_application_email(subject, message, recipient_list):
    if not DEBUG:
        send_mail(subject, message, settings.HRMS_DEFAULT_FROM_EMAIL, recipient_list)
        logging.info("Tour application status email sent")
    


@shared_task
def send_regularization_notification(regularization_id, protocol, domain):
    log = AttendanceLog.objects.get(id=regularization_id)
    user = log.applied_by
    manager = user.reports_to

    def create_email_context(title, content, log, protocol, domain):
        return {
            "title": title,
            "content": content,
            "detail_url": f"{protocol}://{domain}{reverse('event_detail', kwargs={'slug': log.slug})}",
        }

    def send_email(subject, content, recipient):
        context = create_email_context(subject, content, log, protocol, domain)
        message = render_to_string("email/leave_application_email.txt", context)
        send_regularization_email.delay(subject, message, [recipient])

    # Employee email content
    employee_content = (
        f"Dear {user.first_name},\n\n"
        f"Your regularization update. \n\n"
        f"Tour Details:\n"
        f"- {log.from_date} to {log.to_date}  ({log.reg_status}).\n"
        f"- Status: {log.status}\n"
        f"Thank you,\n"
        f"Your HR Team\n\n"
        f"You can review the tour detail at the following link:"
    )
    employee_email = user.official_email if user.official_email else user.email
    send_email("Regularization Status", employee_content, employee_email)

    # Manager email content
    manager_content = (
        f"Dear {manager.first_name} {manager.last_name},\n\n"
        f"A regularization requested by {user.get_full_name()} \n\n"
        f"Tour Details:\n"
        f"- from ({log.from_date}) to ({log.to_date})  has been {log.status}.\n"
        f"- Status: {log.status}\n"
        f"You can review the tour detail at the following link:"
    )
    send_email(
        "Regularization Status",
        manager_content,
        manager.official_email if manager.official_email else manager.email,
    )
    logging.info("Regularization Status email sent")


@shared_task
def send_regularization_email(subject, message, recipient_list):
    if not DEBUG:
        send_mail(subject, message, settings.HRMS_DEFAULT_FROM_EMAIL, recipient_list)
        logging.info("Regularization Status sent")

@shared_task
def populate_attendance_log():
    now = datetime.now()
    from_date = now.strftime('%Y-%m-%d 00:01:00')
    to_date = now.strftime('%Y-%m-%d 23:59:00')
    call_command('pop_att', '--from-date', from_date, '--to-date', to_date)


@shared_task
def send_reminder_email():
    subject = f'Reminder For Attendance Regularization'
    email = EmailMessage(
        subject,
        "It is requested to all the employee the check attendance status(Leave, Tour, Late Coming, Early Going, Mis punching) and take approval for salary finalization if any.",
        settings.DEFAULT_FROM_EMAIL,
        ['all@kasheemilk.com'],
    )
    email.send()
    logging.info(f"reminder mail sent at {timezone.now()}")


def send_greeting_email(obj, occasion_type):
    today = datetime.now().date()
    date_to_check = None
    occasion_name = None
    
    if occasion_type == 'birthday':
        date_to_check = obj.birthday
        occasion_name = WishingCard.BirthdayCard
    elif occasion_type == 'marriage_anniversary':
        date_to_check = obj.marriage_ann
        occasion_name = WishingCard.MarriageAnniversaryCard
    elif occasion_type == 'job_anniversary':
        date_to_check = obj.doj
        occasion_name = WishingCard.JobAnniversaryCard
    
    if date_to_check and date_to_check.day == today.day and date_to_check.month == today.month:
        subject = f'Wishing Happy {occasion_name} {obj.admin.first_name} {obj.admin.last_name}'
        flag = 'Shri' if obj.gender.gender == 'Male' else 'Mis'
        salutation = f"Dear {flag} {obj.admin.first_name} {obj.admin.last_name},<br><br>"
        regards = '<br><br>Regards,<br>HR Team'
        random_card = WishingCard.objects.filter(type=occasion_name).order_by('?').first()
        
        with open(random_card.image.path, 'rb') as f:
            image_data = f.read()
            encoded_image = base64.b64encode(image_data).decode('utf-8')
        
        if occasion_type == 'job_anniversary':
            years = today.year - obj.date_of_joining.year
            anniversary_msg = f"Congratulations on your {ordinal(years)} job anniversary with Kashee!<br><br>"
            html_content = f"<html><body>{salutation}{anniversary_msg}<img style='height:350px;width:200px' src='data:image/jpeg;base64,{encoded_image}' alt='{occasion_name} Card'><br><br>{regards}</body></html>"
        else:
            html_content = f"<html><body>{salutation}<img style='height:350px;width:200px' src='data:image/jpeg;base64,{encoded_image}' alt='{occasion_name} Card'><br><br>{regards}</body></html>"
        
        try:
            emp_email = EmailMultiAlternatives(
                subject,
                '',  # Leave the plain text version empty
                settings.DEFAULT_FROM_EMAIL,
                ['all@kasheemilk.com'],  # Send to employee's email
            )
            emp_email.attach_alternative(html_content, 'text/html')  # Attach HTML content with base64-encoded image
            emp_email.send()
            logging.info(f"Greeting email sent: {timezone.now()}")
        except Exception as e:
            logging.error(f"Error while sending the greeting email: {e}")
            

@shared_task
def send_greeting_emails():
    today = datetime.now().date()
    emp_objs = PersonalDetails.objects.filter(user__is_active=True)
    for obj in emp_objs:
        if obj.birthday and obj.birthday.day == today.day and obj.birthday.month == today.month:
            send_greeting_email(obj, 'birthday')
        if obj.marriage_ann and obj.marriage_ann.day == today.day and obj.marriage_ann.month == today.month:
            send_greeting_email(obj, 'marriage_anniversary')
        if obj.doj and obj.doj.day == today.day and obj.doj.month == today.month:
            send_greeting_email(obj, 'job_anniversary')


def ordinal(n):
    """
    Convert an integer into its ordinal representation:
    1 -> 1st, 2 -> 2nd, 3 -> 3rd, etc.
    """
    if 10 <= n % 100 <= 20:
        suffix = 'th'
    else:
        suffix = {1: 'st', 2: 'nd', 3: 'rd'}.get(n % 10, 'th')
    return str(n) + suffix


def get_database_config():
    DB_NAME = config("DB_NAME")
    mysql_user = config("DB_USER")
    mysql_password = config("DB_PASSWORD")
    mysql_host = config("DB_HOST", default="localhost")
    mysql_port = config("DB_PORT", default="5432")
    return DB_NAME, mysql_user, mysql_password, mysql_host, mysql_port

@shared_task
def backup_database(include_schema=True):
    DB_NAME, mysql_user, mysql_password, mysql_host, mysql_port = get_database_config()
    backup_dir = os.getenv('BACKUP_DIR', "E:/MySQLBackups/DBBACKUP")
    mysqldump_path = 'E:/postgres/16/bin/pg_dump.exe'
    seven_zip_path = 'C:/Program Files/7-Zip/7z.exe'

    backup_name = os.path.join(backup_dir, f'hrms_db_{datetime.now().strftime("%Y-%m-%d_%H-%M-%S")}.sql')
    
    if include_schema:
        mysqldump_cmd = f'"{mysqldump_path}" --user={mysql_user} --password={mysql_password} --host={mysql_host} --port={mysql_port} {DB_NAME} > "{backup_name}"'
    else:
        mysqldump_cmd = f'"{mysqldump_path}" --user={mysql_user} --password={mysql_password} --host={mysql_host} --port={mysql_port} --no-create-info {DB_NAME} > "{backup_name}"'

    backup_zip_name = create_backup(DB_NAME, backup_dir, mysqldump_cmd, backup_name, 'Backup failed: error during dump creation', seven_zip_path)
    
    if backup_zip_name:
        message = f'Database backup successful for the HRMS employee data: {backup_name}'
        dept = Department.objects.get(department='IT')
        emp_emails = PersonalDetails.objects.filter(designation__department=dept).values_list('user__email', flat=True)
        send_backup_email('Database backup successful:', message, emp_emails)
        return True
    return False

def send_backup_email(subject, message, recipients):
    from django.core.mail import EmailMessage
    emp_email = EmailMessage(subject, message, settings.DEFAULT_FROM_EMAIL, recipients)
    logging.info(f"Backup email sent")
    emp_email.send()

def create_backup(DB_NAME, backup_dir, mysqldump_cmd, backup_name, error_message, seven_zip_path):
    if subprocess.call(mysqldump_cmd, shell=True) != 0:
        return False
    backup_zip_name = f'{backup_dir}/{DB_NAME}_{datetime.now().strftime("%Y-%m-%d_%H-%M-%S")}.zip'
    seven_zip_cmd = f'"{seven_zip_path}" a -tzip "{backup_zip_name}" "{backup_name}"'
    if subprocess.call(seven_zip_cmd, shell=True) != 0:
        return False
    os.remove(backup_name)
    return backup_zip_name

