from django.utils.translation import gettext

# App name for notifications
APP_NAME = "product"

# Notification types
NOTIFICATION_TYPE = {
    'PRODUCT_CREATED': 'product_created',
    'PRODUCT_UPDATED': 'product_updated',
    'PRODUCT_DELETED': 'product_deleted',
    'PRICE_CHANGED': 'price_changed',
    'CATEGORY_CHANGED': 'category_changed',
    'BRAND_CHANGED': 'brand_changed'
}

# Notification titles
NOTIFICATION_TITLES = {
    NOTIFICATION_TYPE['PRODUCT_CREATED']: gettext("New Product Created"),
    NOTIFICATION_TYPE['PRODUCT_UPDATED']: gettext("Product Updated"),
    NOTIFICATION_TYPE['PRODUCT_DELETED']: gettext("Product Deleted"),
    NOTIFICATION_TYPE['PRICE_CHANGED']: gettext("Product Price Changed"),
    NOTIFICATION_TYPE['CATEGORY_CHANGED']: gettext("Product Category Changed"),
    NOTIFICATION_TYPE['BRAND_CHANGED']: gettext("Product Brand Changed")
}

# Notification messages
NOTIFICATION_MESSAGES = {
    NOTIFICATION_TYPE['PRODUCT_CREATED']: gettext(
        "New product created: %(name)s (%(sku)s) "
        "Category: %(category)s, Brand: %(brand)s"
    ),
    NOTIFICATION_TYPE['PRODUCT_UPDATED']: gettext(
        "Product updated: %(name)s (%(sku)s) "
        "Changes: %(changes)s"
    ),
    NOTIFICATION_TYPE['PRODUCT_DELETED']: gettext(
        "Product deleted: %(name)s (%(sku)s)"
    ),
    NOTIFICATION_TYPE['PRICE_CHANGED']: gettext(
        "Price changed for %(name)s: "
        "Previous: $%(old_price).2f, New: $%(new_price).2f"
    ),
    NOTIFICATION_TYPE['CATEGORY_CHANGED']: gettext(
        "Category changed for %(name)s: "
        "From %(old_category)s to %(new_category)s"
    ),
    NOTIFICATION_TYPE['BRAND_CHANGED']: gettext(
        "Brand changed for %(name)s: "
        "From %(old_brand)s to %(new_brand)s"
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
    'PRICE': ['Manager', 'Accountant', 'Admin'],
    'CATALOG': ['Manager', 'Stock_Controller', 'Admin']
}