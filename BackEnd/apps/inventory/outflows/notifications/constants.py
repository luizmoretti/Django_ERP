from django.utils.translation import gettext

# App name for notifications
APP_NAME = "outflows"

# Notification types
NOTIFICATION_TYPE = {
    'OUTFLOW_CREATED': 'outflow_created',
    'OUTFLOW_APPROVED': 'outflow_approved',
    'OUTFLOW_REJECTED': 'outflow_rejected',
    'OUTFLOW_CANCELLED': 'outflow_cancelled',
    'OUTFLOW_COMPLETED': 'outflow_completed'
}

# Notification titles
NOTIFICATION_TITLES = {
    NOTIFICATION_TYPE['OUTFLOW_CREATED']: gettext("New Outflow Created"),
    NOTIFICATION_TYPE['OUTFLOW_APPROVED']: gettext("Outflow Approved"),
    NOTIFICATION_TYPE['OUTFLOW_REJECTED']: gettext("Outflow Rejected"),
    NOTIFICATION_TYPE['OUTFLOW_CANCELLED']: gettext("Outflow Cancelled"),
    NOTIFICATION_TYPE['OUTFLOW_COMPLETED']: gettext("Outflow Delivered")
}

# Notification messages
NOTIFICATION_MESSAGES = {
    NOTIFICATION_TYPE['OUTFLOW_CREATED']: gettext(
        "New outflow created: %(quantity)d units of %(product)s "
        "for %(customer)s. Total value: $%(value).2f"
    ),
    NOTIFICATION_TYPE['OUTFLOW_APPROVED']: gettext(
        "Outflow approved: %(quantity)d units of %(product)s "
        "for %(customer)s. Total value: $%(value).2f"
    ),
    NOTIFICATION_TYPE['OUTFLOW_REJECTED']: gettext(
        "Outflow rejected: %(quantity)d units of %(product)s "
        "for %(customer)s. Reason: %(reason)s"
    ),
    NOTIFICATION_TYPE['OUTFLOW_CANCELLED']: gettext(
        "Outflow cancelled: %(quantity)d units of %(product)s "
        "for %(customer)s. Reason: %(reason)s"
    ),
    NOTIFICATION_TYPE['OUTFLOW_COMPLETED']: gettext(
        "Outflow completed: %(quantity)d units of %(product)s "
        "to %(customer)s. Delivery date: %(delivery_date)s"
    )
}

# Notification severity types
SEVERITY_TYPES = {
    'INFO': 'info',
    'WARNING': 'warning'
}

# User types that should receive notifications
RECIPIENT_TYPES = {
    'DEFAULT': ['Stock_Controller', 'Manager', 'Admin'],
    'APPROVAL': ['Manager', 'Owner', 'CEO', 'Admin'],
    'DELIVERY': ['Deliveryman', 'Driver', 'Manager'],
    'WAREHOUSE': ['Stock_Controller', 'Stocker', 'Manager']
}