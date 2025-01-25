from django.utils.translation import gettext_lazy as _

# User Types - Hierarchical Organization
USER_TYPE_CHOICES = (
    # Executive Level - High-level management and ownership
    ('CEO', _('CEO')),
    ('Owner', _('Owner')),
    ('Admin', _('Admin')),

    # Management Level - Mid-level management and specialized roles
    ('Manager', _('Manager')),
    ('HR', _('HR')),
    ('Accountant', _('Accountant')),

    # Operational Level - Day-to-day operations staff
    ('Employee', _('Employee')),
    ('Stock_Controller', _('Stock Controller')),
    ('Stocker', _('Stocker')),
    ('Salesman', _('Salesman')),
    ('Driver', _('Driver')),
    ('Deliveryman', _('Deliveryman')),

    # External Users - Non-employee stakeholders
    ('Customer', _('Customer')),
    ('Supplier', _('Supplier')),
)

# HR Payment Intervals
# Constants for payment intervals
PAYMENT_INTERVAL_CHOICES = [
    ('Daily', _('Daily')),
    ('Weekly', _('Weekly')),
    ('Biweekly', _('Biweekly')),
    ('Monthly', _('Monthly')),
]

# Business Days
BUSINESS_DAY_CHOICES = [
        (1, _('1st Business Day')), # Monday
        (2, _('2nd Business Day')), # Tuesday
        (3, _('3rd Business Day')), # Wednesday
        (4, _('4th Business Day')), # Thursday
        (5, _('5th Business Day')), # Friday
    ]

COMPANIE_TYPE_CHOICES = [
    ('Headquarters', _('Headquarters')),
    ('Subsidiary', _('Subsidiary')),
]


COUNTRY_CHOICES = [
    ('USA', _('USA')),
    ('Canada', _('Canada')),
    ('Mexico', _('Mexico')),
    ('Brazil', _('Brazil')),
    ('Argentina', _('Argentina')),
    ('Chile', _('Chile')),
    ('Colombia', _('Colombia')),
    ('Ecuador', _('Ecuador')),
    ('Peru', _('Peru')),
    ('Paraguay', _('Paraguay')),
    ('Venezuela', _('Venezuela')),
    ('Other', _('Other')),
]