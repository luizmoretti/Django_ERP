# Notification types
NOTIFICATION_TYPE = {
    'DELIVERY_CREATED': 'delivery_created',
    'DELIVERY_UPDATED': 'delivery_updated',
    'DELIVERY_STATUS_CHANGED': 'delivery_status_changed',
    'DELIVERY_LOCATION_UPDATED': 'delivery_location_updated',
    'DELIVERY_STARTED': 'delivery_started',
    'DELIVERY_COMPLETED': 'delivery_completed',
    'DELIVERY_DELAYED': 'delivery_delayed',
    'DELIVERY_APPROACHING': 'delivery_approaching',
}

# Notification titles
NOTIFICATION_TITLES = {
    NOTIFICATION_TYPE['DELIVERY_CREATED']: 'New Delivery Created',
    NOTIFICATION_TYPE['DELIVERY_UPDATED']: 'Delivery Updated',
    NOTIFICATION_TYPE['DELIVERY_STATUS_CHANGED']: 'Delivery Status Changed',
    NOTIFICATION_TYPE['DELIVERY_LOCATION_UPDATED']: 'Delivery Location Updated',
    NOTIFICATION_TYPE['DELIVERY_STARTED']: 'Delivery Started',
    NOTIFICATION_TYPE['DELIVERY_COMPLETED']: 'Delivery Completed',
    NOTIFICATION_TYPE['DELIVERY_DELAYED']: 'Delivery Delayed',
    NOTIFICATION_TYPE['DELIVERY_APPROACHING']: 'Delivery Approaching',
}

# Notification messages
NOTIFICATION_MESSAGES = {
    NOTIFICATION_TYPE['DELIVERY_CREATED']: 'A new delivery #{} has been created',
    NOTIFICATION_TYPE['DELIVERY_UPDATED']: 'Delivery #{} has been updated',
    NOTIFICATION_TYPE['DELIVERY_STATUS_CHANGED']: 'Delivery #{} status changed to {}',
    NOTIFICATION_TYPE['DELIVERY_LOCATION_UPDATED']: 'Delivery #{} location has been updated',
    NOTIFICATION_TYPE['DELIVERY_STARTED']: 'Delivery #{} has started',
    NOTIFICATION_TYPE['DELIVERY_COMPLETED']: 'Delivery #{} has been completed',
    NOTIFICATION_TYPE['DELIVERY_DELAYED']: 'Delivery #{} is delayed',
    NOTIFICATION_TYPE['DELIVERY_APPROACHING']: 'Delivery #{} is approaching its destination',
}

# Notification severity types
SEVERITY_TYPES = {
    NOTIFICATION_TYPE['DELIVERY_CREATED']: 'info',
    NOTIFICATION_TYPE['DELIVERY_UPDATED']: 'info',
    NOTIFICATION_TYPE['DELIVERY_STATUS_CHANGED']: 'info',
    NOTIFICATION_TYPE['DELIVERY_LOCATION_UPDATED']: 'info',
    NOTIFICATION_TYPE['DELIVERY_STARTED']: 'success',
    NOTIFICATION_TYPE['DELIVERY_COMPLETED']: 'success',
    NOTIFICATION_TYPE['DELIVERY_DELAYED']: 'warning',
    NOTIFICATION_TYPE['DELIVERY_APPROACHING']: 'info',
}

# Recipient types for different notification types
RECIPIENT_TYPES = {
    'DEFAULT': ['Owner', 'CEO', 'Admin', 'Manager'],
    'DELIVERY_ADMIN': ['Admin', 'Manager'],
    'DELIVERY_OPERATOR': ['Manager', 'Driver'],
    'CUSTOMER': ['Customer'],
}