from django.utils.translation import gettext_lazy as _

EARLY_GOING = "early going"
LATE_COMING = "late coming"
MIS_PUNCHING = "mis punching"
PRE_APPROVAL = "pre approval"
POST_APPROVAL = "post approval"
ON_ROLE = "on role"
OFF_ROLE = "off role"
FULL_DAY, FIRST_HALF, SECOND_HALF = "1", "2", "3"

SALUTATION_CHOICES = [
    ("Mr.", "Mr."),
    ("Ms.", "Ms."),
    ("Mrs.", "Mrs."),
    ("Dr.", "Dr."),
    ("Prof.", "Prof."),
    ("Er.", "Er."),
]


HALF_DAY = "Half Day"
PRESENT = "Present"
ABSENT = "Absent"

UP, CL, SL, EL, ML, CO = (
    "Unpaid Leave (LWP)",
    "Casual Leave (CL)",
    "Sick Leave (SL)",
    "Earned Leave (EL)",
    "Maternity Leave (ML)",
    "Comp OFF",
)

PENDING = "pending"
SENT = "sent"
FAILED = "failed"
APPROVED = "approved"
CANCELLED = "cancelled"
PENDING_CANCELLATION = "pending_cancellation"
REJECTED = "rejected"
COMPLETED = "completed"
EXTENDED = "extended"
RECOMMEND = "recommended"
NOT_RECOMMEND = "not recommended"

ATTENDANCE_REGULARISED_STATUS_CHOICES = [
    (EARLY_GOING, _("Early Going")),
    (LATE_COMING, _("Late Coming")),
    (MIS_PUNCHING, _("Mis Punching")),
]

ATTENDANCE_STATUS_CHOICES = [
    (HALF_DAY, _("Half Day")),
    (PRESENT, _("Present")),
    (ABSENT, _("Absent")),
]

ATTENDANCE_LOG_STATUS_CHOICES = [
    (PENDING, _("Pending")),
    (APPROVED, _("Approved")),
    (REJECTED, _("Rejected")),
    (RECOMMEND, _("Recommended")),
    (NOT_RECOMMEND, _("Not Recommended")),
]

TOUR_STATUS_CHOICES = [
    (PENDING, _("Pending")),
    (APPROVED, _("Approved")),
    (REJECTED, _("Rejected")),
    (COMPLETED, _("Completed")),
    (CANCELLED, _("Cancelled")),
    (EXTENDED, _("Extended")),
    (PENDING_CANCELLATION, _("Pending Cancellation")),
]

APPROVAL_TYPE_CHOICES = [
    (PRE_APPROVAL, _("Pre Approval")),
    (POST_APPROVAL, _("Post Approval")),
]

LEAVE_STATUS_CHOICES = [
    (PENDING, _("Pending")),
    (APPROVED, _("Approved")),
    (REJECTED, _("Rejected")),
    (CANCELLED, _("Cancelled")),
    (PENDING_CANCELLATION, _("Pending Cancellation")),
    (RECOMMEND, _("Recommended")),
    (NOT_RECOMMEND, _("Not Recommended")),
]

START_LEAVE_TYPE_CHOICES = [
    (FULL_DAY, _("Full Day")),
    (FIRST_HALF, _("First Half (Morning)")),
    (SECOND_HALF, _("Second Half (Afternoon)")),
]


LEAVE_TYPE_CHOICES = [
    (UP, _("Unpaid Leave (LWP)")),
    (CL, _("Casual Leave (CL)")),
    (SL, _("Sick Leave (SL)")),
    (EL, _("Earned Leave (EL)")),
    (ML, _("Maternity Leave (ML)")),
    (CO, _("Comp OFF (CO)")),
]


SENT_MAIL_STATUS_CHOICES = (
    (PENDING, _("Pending")),
    (SENT, _("Sent")),
    (FAILED, _("Failed")),
)


ROLE_CHOICES = [
    (ON_ROLE, "On-Role"),
    (OFF_ROLE, "Off-Role"),
]

LOCATION_CHOICES = [
    (ON_ROLE, "On-Role"),
    (OFF_ROLE, "Off-Role"),
]
HEAD_OFFICE = "head_office"
CLUSTER_OFFICE = "cluster_office"
MCC = "mcc"
BMC = "bmc"
MPP = "mpp"

OFFICE_TYPE_CHOICES = [
    (HEAD_OFFICE, "Head Office"),
    (CLUSTER_OFFICE, "Cluster Office"),
    (MCC, "MCC"),
    (BMC, "BMC"),
    (MPP, "BMC"),
]

OPEN = "open"
CLAIMED = "claimed"
EXPIRED = "expired"

CO_STATUS_CHOICES = [
    (OPEN, "Open"),
    (CLAIMED, "Claimed"),
    (EXPIRED, "Expired"),
    (REJECTED, "Rejected"),
]

LEAVE_STATUS = "leave_status"
TOUR_STATUS = "tour_status"
CO_STATUS = "comp_off_status"
CHAT = "chat"
ATTENDANCE_REGULARISATION = "attendance_reg"

NOTIFICATION_TYPES = [
    (LEAVE_STATUS, "Leave Status"),
    (TOUR_STATUS, "Tour Status"),
    (CO_STATUS, "Compensatory Off Status"),
    (CHAT, "Chat"),
    (ATTENDANCE_REGULARISATION, "Attendance Regularization"),
]


customColorPalette = [
    {"color": "hsl(4, 90%, 58%)", "label": "Red"},
    {"color": "hsl(340, 82%, 52%)", "label": "Pink"},
    {"color": "hsl(291, 64%, 42%)", "label": "Purple"},
    {"color": "hsl(262, 52%, 47%)", "label": "Deep Purple"},
    {"color": "hsl(231, 48%, 48%)", "label": "Indigo"},
    {"color": "hsl(207, 90%, 54%)", "label": "Blue"},
]

# CKEDITOR_5_CUSTOM_CSS = 'path_to.css' # optional
CKEDITOR_5_FILE_STORAGE = "hrms_app.custom_storage.CustomStorage"

CKEDITOR_5_CONFIGS = {
    "default": {
        "toolbar": [
            "heading",
            "|",
            "bold",
            "italic",
            "link",
            "bulletedList",
            "numberedList",
            "blockQuote",
            "imageUpload",
        ],
    },
    "extends": {
        "blockToolbar": [
            "paragraph",
            "heading1",
            "heading2",
            "heading3",
            "|",
            "bulletedList",
            "numberedList",
            "|",
            "blockQuote",
        ],
        "toolbar": [
            "heading",
            "|",
            "outdent",
            "indent",
            "|",
            "bold",
            "italic",
            "link",
            "underline",
            "strikethrough",
            "code",
            "subscript",
            "superscript",
            "highlight",
            "|",
            "codeBlock",
            "sourceEditing",
            "insertImage",
            "bulletedList",
            "numberedList",
            "todoList",
            "|",
            "blockQuote",
            "imageUpload",
            "|",
            "fontSize",
            "fontFamily",
            "fontColor",
            "fontBackgroundColor",
            "mediaEmbed",
            "removeFormat",
            "insertTable",
        ],
        "image": {
            "toolbar": [
                "imageTextAlternative",
                "|",
                "imageStyle:alignLeft",
                "imageStyle:alignRight",
                "imageStyle:alignCenter",
                "imageStyle:side",
                "|",
            ],
            "styles": [
                "full",
                "side",
                "alignLeft",
                "alignRight",
                "alignCenter",
            ],
        },
        "table": {
            "contentToolbar": [
                "tableColumn",
                "tableRow",
                "mergeTableCells",
                "tableProperties",
                "tableCellProperties",
            ],
            "tableProperties": {
                "borderColors": customColorPalette,
                "backgroundColors": customColorPalette,
            },
            "tableCellProperties": {
                "borderColors": customColorPalette,
                "backgroundColors": customColorPalette,
            },
        },
        "heading": {
            "options": [
                {
                    "model": "paragraph",
                    "title": "Paragraph",
                    "class": "ck-heading_paragraph",
                },
                {
                    "model": "heading1",
                    "view": "h1",
                    "title": "Heading 1",
                    "class": "ck-heading_heading1",
                },
                {
                    "model": "heading2",
                    "view": "h2",
                    "title": "Heading 2",
                    "class": "ck-heading_heading2",
                },
                {
                    "model": "heading3",
                    "view": "h3",
                    "title": "Heading 3",
                    "class": "ck-heading_heading3",
                },
            ]
        },
    },
    "list": {
        "properties": {
            "styles": "true",
            "startIndex": "true",
            "reversed": "true",
        }
    },
}


CK_EDITOR_5_UPLOAD_FILE_VIEW_NAME = "custom_upload_file"


handler403 = "hrms_app.views.custom_permission_denied_view"

from datetime import timedelta

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "DEFAULT_FILTER_BACKENDS": ["django_filters.rest_framework.DjangoFilterBackend"],
    # 'DEFAULT_PERMISSION_CLASSES': (
    #     'rest_framework.permissions.IsAuthenticated',
    # ),
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 10,  # Number of items per page
}

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(days=60),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=90),
    "ROTATE_REFRESH_TOKENS": False,
    "BLACKLIST_AFTER_ROTATION": False,
    "UPDATE_LAST_LOGIN": True,
    "ALGORITHM": "HS256",
    "LEEWAY": 0,
    "AUTH_HEADER_TYPES": ("Bearer",),
    "AUTH_HEADER_NAME": "HTTP_AUTHORIZATION",
    "USER_ID_FIELD": "id",
    "USER_ID_CLAIM": "user_id",
    "USER_AUTHENTICATION_RULE": "rest_framework_simplejwt.authentication.default_user_authentication_rule",
    "AUTH_TOKEN_CLASSES": ("rest_framework_simplejwt.tokens.AccessToken",),
    "TOKEN_TYPE_CLAIM": "token_type",
    "TOKEN_USER_CLASS": "rest_framework_simplejwt.models.TokenUser",
}
