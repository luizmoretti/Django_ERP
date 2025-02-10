from django.utils.translation import gettext

# App name for notifications
APP_NAME = "inflows"

# Notification types
NOTIFICATION_TYPE = {
    'INFLOW_RECEIVED': 'inflow_received',
    'INFLOW_APPROVED': 'inflow_approved',
    'INFLOW_REJECTED': 'inflow_rejected',
    'INFLOW_CANCELLED': 'inflow_cancelled'
}

# Notification titles
NOTIFICATION_TITLES = {
    NOTIFICATION_TYPE['INFLOW_RECEIVED']: gettext("New Inflow Received"),
    NOTIFICATION_TYPE['INFLOW_APPROVED']: gettext("Inflow Approved"),
    NOTIFICATION_TYPE['INFLOW_REJECTED']: gettext("Inflow Rejected"),
    NOTIFICATION_TYPE['INFLOW_CANCELLED']: gettext("Inflow Cancelled")
}

# Notification messages
NOTIFICATION_MESSAGES = {
    NOTIFICATION_TYPE['INFLOW_RECEIVED']: gettext(
        "New inflow received: %(quantity)d units of %(product)s "
        "from %(supplier)s. Total value: $%(value).2f"
    ),
    NOTIFICATION_TYPE['INFLOW_APPROVED']: gettext(
        "Inflow approved: %(quantity)d units of %(product)s "
        "from %(supplier)s. Total value: $%(value).2f"
    ),
    NOTIFICATION_TYPE['INFLOW_REJECTED']: gettext(
        "Inflow rejected: %(quantity)d units of %(product)s "
        "from %(supplier)s. Reason: %(reason)s"
    ),
    NOTIFICATION_TYPE['INFLOW_CANCELLED']: gettext(
        "Inflow cancelled: %(quantity)d units of %(product)s "
        "from %(supplier)s. Reason: %(reason)s"
    )
}

# Notification severity types
SEVERITY_TYPES = {
    'INFO': 'info',
    'WARNING': 'warning'
}