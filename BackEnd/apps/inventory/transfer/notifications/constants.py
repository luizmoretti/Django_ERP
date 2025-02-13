from django.utils.translation import gettext

# App name for notifications
APP_NAME = "transfer"

# Notification types
NOTIFICATION_TYPE = {
    'TRANSFER_CREATED': 'transfer_created',
    'TRANSFER_APPROVED': 'transfer_approved',
    'TRANSFER_REJECTED': 'transfer_rejected',
    'TRANSFER_CANCELLED': 'transfer_cancelled',
    'TRANSFER_COMPLETED': 'transfer_completed'
}

# Notification titles
NOTIFICATION_TITLES = {
    NOTIFICATION_TYPE['TRANSFER_CREATED']: gettext("New Transfer Created"),
    NOTIFICATION_TYPE['TRANSFER_APPROVED']: gettext("Transfer Approved"),
    NOTIFICATION_TYPE['TRANSFER_REJECTED']: gettext("Transfer Rejected"),
    NOTIFICATION_TYPE['TRANSFER_CANCELLED']: gettext("Transfer Cancelled"),
    NOTIFICATION_TYPE['TRANSFER_COMPLETED']: gettext("Transfer Completed")
}

# Notification messages
NOTIFICATION_MESSAGES = {
    NOTIFICATION_TYPE['TRANSFER_CREATED']: gettext(
        "New transfer created: %(quantity)d units of %(product)s "
        "from %(origin)s to %(destiny)s"
    ),
    NOTIFICATION_TYPE['TRANSFER_APPROVED']: gettext(
        "Transfer approved: %(quantity)d units of %(product)s "
        "from %(origin)s to %(destiny)s"
    ),
    NOTIFICATION_TYPE['TRANSFER_REJECTED']: gettext(
        "Transfer rejected: %(quantity)d units of %(product)s "
        "from %(origin)s to %(destiny)s. Reason: %(reason)s"
    ),
    NOTIFICATION_TYPE['TRANSFER_CANCELLED']: gettext(
        "Transfer cancelled: %(quantity)d units of %(product)s "
        "from %(origin)s to %(destiny)s. Reason: %(reason)s"
    ),
    NOTIFICATION_TYPE['TRANSFER_COMPLETED']: gettext(
        "Transfer completed: %(quantity)d units of %(product)s "
        "from %(origin)s to %(destiny)s"
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
    'WAREHOUSE': ['Stock_Controller', 'Stocker', 'Manager']
}