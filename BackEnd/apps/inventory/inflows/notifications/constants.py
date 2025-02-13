from django.utils.translation import gettext

# App name for notifications
APP_NAME = "inflows"

# Notification types
NOTIFICATION_TYPE = {
    'INFLOW_CREATED': 'inflow_created',
    'INFLOW_UPDATED': 'inflow_updated',
    'INFLOW_APPROVED': 'inflow_approved',
    'INFLOW_REJECTED': 'inflow_rejected',
    'INFLOW_DELETED': 'inflow_deleted',
    'STOCK_UPDATED': 'stock_updated',
    'LOW_STOCK_ALERT': 'low_stock_alert'
}

# Notification titles
NOTIFICATION_TITLES = {
    NOTIFICATION_TYPE['INFLOW_CREATED']: gettext("New Inflow Created"),
    NOTIFICATION_TYPE['INFLOW_UPDATED']: gettext("Inflow Updated"),
    NOTIFICATION_TYPE['INFLOW_APPROVED']: gettext("Inflow Approved"),
    NOTIFICATION_TYPE['INFLOW_REJECTED']: gettext("Inflow Rejected"),
    NOTIFICATION_TYPE['INFLOW_DELETED']: gettext("Inflow Deleted"),
    NOTIFICATION_TYPE['STOCK_UPDATED']: gettext("Stock Updated"),
    NOTIFICATION_TYPE['LOW_STOCK_ALERT']: gettext("Low Stock Alert")
}

# Notification messages
NOTIFICATION_MESSAGES = {
    NOTIFICATION_TYPE['INFLOW_CREATED']: gettext(
        "New inflow created from %(origin)s to %(destiny)s the total items are %(items_count)d and the total value is $%(total_value).2f"
    ),
    NOTIFICATION_TYPE['INFLOW_UPDATED']: gettext(
        "Inflow updated from %(origin)s to %(destiny)s, the total items are now %(items_count)d and the total value is $%(total_value).2f"
    ),
    NOTIFICATION_TYPE['INFLOW_APPROVED']: gettext(
        "Inflow Approved by: %(approved_by)s for origin %(origin)s and destiny %(destiny)s, the total items are %(items_count)d and the total value is $%(total_value).2f"
    ),
    NOTIFICATION_TYPE['INFLOW_REJECTED']: gettext(
        "Inflow Rejected by: %(rejected_by)s for origin %(origin)s and destiny %(destiny)s, the total items are %(items_count)d. Reason: %(reason)s"
    ),
    NOTIFICATION_TYPE['INFLOW_DELETED']: gettext(
        "Inflow deleted from %(origin)s to %(destiny)s by %(deleted_by)s"
    ),
    NOTIFICATION_TYPE['STOCK_UPDATED']: gettext(
        "Stock updated in warehouse %(warehouse)s for product %(product)s, new quantity is %(new_quantity)d (previous: %(previous_quantity)d)"
    ),
    NOTIFICATION_TYPE['LOW_STOCK_ALERT']: gettext(
        "Low stock alert in warehouse %(warehouse)s for product %(product)s, current quantity is %(current_quantity)d (minimum: %(min_quantity)d)"
    )
}

# Notification severity types
SEVERITY_TYPES = {
    'INFO': 'info',
    'WARNING': 'warning',
    'ERROR': 'error'
}

# Notification priorities
NOTIFICATION_PRIORITIES = {
    NOTIFICATION_TYPE['INFLOW_CREATED']: 'normal',
    NOTIFICATION_TYPE['INFLOW_UPDATED']: 'normal',
    NOTIFICATION_TYPE['INFLOW_APPROVED']: 'high',
    NOTIFICATION_TYPE['INFLOW_REJECTED']: 'high',
    NOTIFICATION_TYPE['INFLOW_DELETED']: 'high',
    NOTIFICATION_TYPE['STOCK_UPDATED']: 'normal',
    NOTIFICATION_TYPE['LOW_STOCK_ALERT']: 'high'
}

# Recipient types for each notification
RECIPIENT_TYPES = {
    NOTIFICATION_TYPE['INFLOW_CREATED']: ['Stock_Controller', 'Manager', 'Admin'],
    NOTIFICATION_TYPE['INFLOW_UPDATED']: ['Stock_Controller', 'Manager', 'Admin'],
    NOTIFICATION_TYPE['INFLOW_APPROVED']: ['Stock_Controller', 'Manager', 'Owner', 'CEO', 'Admin'],
    NOTIFICATION_TYPE['INFLOW_REJECTED']: ['Stock_Controller', 'Manager', 'Owner', 'CEO', 'Admin'],
    NOTIFICATION_TYPE['INFLOW_DELETED']: ['Stock_Controller', 'Manager', 'Owner', 'CEO', 'Admin'],
    NOTIFICATION_TYPE['STOCK_UPDATED']: ['Stock_Controller', 'Stocker', 'Manager'],
    NOTIFICATION_TYPE['LOW_STOCK_ALERT']: ['Stock_Controller', 'Manager', 'Admin', 'Owner', 'CEO']
}