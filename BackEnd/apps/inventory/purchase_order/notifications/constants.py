from django.utils.translation import gettext

# App name for notifications
APP_NAME = "purchase_order"

# Notification types
NOTIFICATION_TYPE = {
    'ORDER_CREATED': 'order_created',
    'ORDER_UPDATED': 'order_updated',
    'ORDER_DELETED': 'order_deleted',
    'ORDER_STATUS_CHANGED': 'order_status_changed',
    'ITEM_ADDED': 'item_added',
    'ITEM_UPDATED': 'item_updated',
    'ITEM_DELETED': 'item_deleted',
    'ITEM_QUANTITY_CHANGED': 'item_quantity_changed',
    'ITEM_PRICE_CHANGED': 'item_price_changed'
}

# Notification titles
NOTIFICATION_TITLES = {
    NOTIFICATION_TYPE['ORDER_CREATED']: gettext("New Purchase Order Created"),
    NOTIFICATION_TYPE['ORDER_UPDATED']: gettext("Purchase Order Updated"),
    NOTIFICATION_TYPE['ORDER_DELETED']: gettext("Purchase Order Deleted"),
    NOTIFICATION_TYPE['ORDER_STATUS_CHANGED']: gettext("Purchase Order Status Changed"),
    NOTIFICATION_TYPE['ITEM_ADDED']: gettext("Item Added to Purchase Order"),
    NOTIFICATION_TYPE['ITEM_UPDATED']: gettext("Purchase Order Item Updated"),
    NOTIFICATION_TYPE['ITEM_DELETED']: gettext("Item Removed from Purchase Order"),
    NOTIFICATION_TYPE['ITEM_QUANTITY_CHANGED']: gettext("Item Quantity Changed"),
    NOTIFICATION_TYPE['ITEM_PRICE_CHANGED']: gettext("Item Price Changed")
}

# Notification messages
NOTIFICATION_MESSAGES = {
    NOTIFICATION_TYPE['ORDER_CREATED']: gettext(
        "New purchase order #%(order_number)s created for %(supplier)s. "
        "Total value: $%(total).2f"
    ),
    NOTIFICATION_TYPE['ORDER_UPDATED']: gettext(
        "Purchase order #%(order_number)s updated. "
        "Total value: $%(total).2f"
    ),
    NOTIFICATION_TYPE['ORDER_DELETED']: gettext(
        "Purchase order #%(order_number)s for %(supplier)s was deleted."
    ),
    NOTIFICATION_TYPE['ORDER_STATUS_CHANGED']: gettext(
        "Purchase order #%(order_number)s status changed from %(old_status)s to %(new_status)s."
    ),
    NOTIFICATION_TYPE['ITEM_ADDED']: gettext(
        "%(product)s added to purchase order #%(order_number)s. "
        "Quantity: %(quantity)d. Total order value: $%(total).2f"
    ),
    NOTIFICATION_TYPE['ITEM_UPDATED']: gettext(
        "%(product)s updated in purchase order #%(order_number)s. "
        "Quantity: %(quantity)d. Total order value: $%(total).2f"
    ),
    NOTIFICATION_TYPE['ITEM_DELETED']: gettext(
        "%(product)s removed from purchase order #%(order_number)s."
    ),
    NOTIFICATION_TYPE['ITEM_QUANTITY_CHANGED']: gettext(
        "%(product)s quantity changed in purchase order #%(order_number)s. "
        "Old: %(old_quantity)d, New: %(new_quantity)d. Total order value: $%(total).2f"
    ),
    NOTIFICATION_TYPE['ITEM_PRICE_CHANGED']: gettext(
        "%(product)s price changed in purchase order #%(order_number)s. "
        "Old: $%(old_price).2f, New: $%(new_price).2f. Total order value: $%(total).2f"
    )
}

# Notification severity types
SEVERITY_TYPES = {
    'INFO': 'info',
    'WARNING': 'warning',
    'ERROR': 'error'
}

# Recipient types
RECIPIENT_TYPES = {
    'DEFAULT': ['Admin', 'Owner', 'CEO'],
    'ORDER': ['Owner', 'CEO', 'Admin', 'Manager'],
    'ITEM': ['Owner', 'CEO', 'Admin', 'Manager'],
    'PRICE': ['Owner', 'CEO', 'Admin', 'Manager']
}
