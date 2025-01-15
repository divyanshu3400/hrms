import xml.etree.ElementTree as ET
from collections import defaultdict
from datetime import datetime, timedelta
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from hrms_app.models import Holiday, LockStatus
from rest_framework.response import Response
from django.core.exceptions import PermissionDenied
import logging
import requests


# Set up logging configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),  # Output to console
        # Uncomment the following line to log to a file:
        # logging.FileHandler('api_logs.log')  # Output to a file
    ]
)

def send_email(subject, template_name, context, from_email, recipient_list):
    """
    Send an email with both plain text and HTML content.

    :param subject: Subject of the email.
    :param template_name: The base name of the email template (without extension).
    :param context: Context data to render the template.
    :param from_email: Sender email address.
    :param recipient_list: List of recipient email addresses.
    """
    html_message = render_to_string(f"{template_name}.html", context)
    plain_message = strip_tags(html_message)

    send_mail(
        subject,
        plain_message,
        from_email,
        recipient_list,
        # html_message=html_message,
    )




def call_soap_api(device_instance, from_date, to_date):
    url = device_instance.api_link
    headers = {"Content-Type": "text/xml"}
    params = {"op": "GetTransactionsLog"}
    attendance_start_date = device_instance.from_date if from_date is None else from_date
    attendance_to_date = device_instance.to_date if to_date is None else to_date
    body = f"""<?xml version="1.0" encoding="utf-8"?>
    <soap:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
        <soap:Body>
            <GetTransactionsLog xmlns="http://tempuri.org/">
                <FromDateTime>{attendance_start_date}</FromDateTime>
                <ToDateTime>{attendance_to_date}</ToDateTime>
                <SerialNumber>{device_instance.serial_number}</SerialNumber>
                <UserName>{device_instance.username}</UserName>
                <UserPassword>{device_instance.password}</UserPassword>
                <strDataList>string</strDataList>
            </GetTransactionsLog>
        </soap:Body>
    </soap:Envelope>
    """

    try:
        response = requests.post(url, params=params, data=body, headers=headers)
        response.raise_for_status()  # This will raise an exception if the response status code is not 200
    except requests.exceptions.RequestException as e:
        logging.error(f"Request failed: {e}")
        return None

    if response.status_code == 200:
        try:
            root = ET.fromstring(response.content)

            # Extracting data from the response
            log_result = root.find(".//{http://tempuri.org/}GetTransactionsLogResult").text
            str_data_list = root.find(".//{http://tempuri.org/}strDataList").text

            # Dictionary to store grouped data
            grouped_data = defaultdict(lambda: defaultdict(list))

            # Splitting and processing each line of str_data_list
            for line in str_data_list.strip().split("\n"):
                parts = line.split()
                if len(parts) >= 2:
                    emp_code = parts[0]
                    log_time_str = " ".join(parts[1:])  # Join the remaining parts as log_time_str

                    try:
                        if not device_instance.include_seconds:
                            # Remove the seconds part if present
                            log_time_str = log_time_str.rsplit(":", 1)[0]
                            time_format = "%Y-%m-%d %H:%M"
                        else:
                            time_format = "%Y-%m-%d %H:%M:%S"

                        log_time = datetime.strptime(log_time_str, time_format)

                        date_key = log_time.date()
                        grouped_data[emp_code][date_key].append(log_time)
                    except ValueError as e:
                        logging.warning(f"Issue parsing line: {line}. Error: {e}")
                else:
                    logging.warning(f"Issue parsing line: {line}. Insufficient data.")

            return grouped_data
        except Exception as e:
            logging.error(f"Error processing XML response: {e}")
            return None
    else:
        logging.error(f"Error: Response returned with status code {response.status_code}")
        return None


def is_weekend(date):
    return date.weekday() == 6


def is_holiday(date):
    return Holiday.objects.filter(start_date=date).exists()


def get_non_working_days(start, end):
    print(f"Getting non working days between: {start} & {end}")
    non_working_days = 0
    for n in range((end - start).days + 1):
        day = start + timedelta(n)
        if is_weekend(day) or is_holiday(day):
            non_working_days += 1
    return non_working_days


def create_response(
    status: str, message: str, data: dict = None, status_code: int = 200
) -> Response:
    response_data = {"status": status, "message": message, "data": data}
    return Response(response_data, status=status_code)



def check_lock_status(instance_date=None):
    """
    Checks if the global lock is active for a specific date.
    The lock applies based on the `from_date` and `to_date` range.
    """
    if instance_date is None:
        instance_date = (
            datetime.now()
        )  # Default to today's date if no instance date is provided
    # Query to find a lock status where instance_date falls between from_date and to_date
    lock_status = LockStatus.objects.filter(
        from_date__lte=instance_date, to_date__gte=instance_date, is_locked="locked"
    ).first()

    if lock_status:
        raise PermissionDenied(
            f"Action is locked for the period from {lock_status.from_date} to {lock_status.to_date}. "
            f"Reason: {lock_status.reason or 'No reason provided'}"
        )
