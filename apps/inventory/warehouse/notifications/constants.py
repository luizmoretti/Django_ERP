from django.utils.translation import gettext

# App name for notifications
APP_NAME = "warehouse"

# Notification types
NOTIFICATION_TYPE = {
    'LOW_STOCK': 'low_stock',
    'OUT_OF_STOCK': 'out_of_stock',
    'STOCK_REPLENISHED': 'stock_replenished',
    'STOCK_ADJUSTED': 'stock_adjusted'
}

# Notification titles
NOTIFICATION_TITLES = {
    NOTIFICATION_TYPE['LOW_STOCK']: gettext("Low Stock Alert"),
    NOTIFICATION_TYPE['OUT_OF_STOCK']: gettext("Out of Stock Alert"),
    NOTIFICATION_TYPE['STOCK_REPLENISHED']: gettext("Stock Replenished"),
    NOTIFICATION_TYPE['STOCK_ADJUSTED']: gettext("Stock Adjusted")
}

# Notification messages
NOTIFICATION_MESSAGES = {
    NOTIFICATION_TYPE['LOW_STOCK']: gettext(
        "%(severity)s: Product %(product)s in %(warehouse)s has low stock. "
        "Current: %(current)d units (%(percentage).1f%% of minimum stock)"
    ),
    NOTIFICATION_TYPE['OUT_OF_STOCK']: gettext(
        "Critical: Product %(product)s in %(warehouse)s is out of stock. "
        "Current: %(current)d units"
    ),
    NOTIFICATION_TYPE['STOCK_REPLENISHED']: gettext(
        "Stock replenished for %(product)s in %(warehouse)s. "
        "New quantity: %(current)d units"
    ),
    NOTIFICATION_TYPE['STOCK_ADJUSTED']: gettext(
        "Stock adjusted for %(product)s in %(warehouse)s. "
        "Previous: %(previous)d, New: %(current)d"
    )
}

# Notification severity thresholds (percentage of minimum stock)
SEVERITY_THRESHOLDS = {
    'CRITICAL': 50,  # ≤ 50% of minimum stock
    'WARNING': 90,   # ≤ 90% of minimum stock
    'INFO': 100      # > 90% of minimum stock
}

# Notification severity types
SEVERITY_TYPES = {
    'CRITICAL': 'critical',
    'WARNING': 'warning',
    'INFO': 'info'
}

# Severity labels for messages
SEVERITY_LABELS = {
    SEVERITY_TYPES['CRITICAL']: gettext("Critical Alert"),
    SEVERITY_TYPES['WARNING']: gettext("Warning"),
    SEVERITY_TYPES['INFO']: gettext("Notice")
}