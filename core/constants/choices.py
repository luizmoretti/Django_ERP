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
PAYROLL_CHOICES = [
    ('Daily', _('Daily')),
    ('Weekly', _('Weekly')),
    ('Biweekly', _('Biweekly')),
    ('Monthly', _('Monthly')),
]

# Constants for payment types
PAYMENT_CHOICES = [
        ('Hour', _('By Hour')),
        ('Day', _('By Day')),
    ]

PAYROLL_STATUS_CHOICES = [
    ('Pending', _('Pending')),
    ('Paid', _('Paid')),
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

STATE_CHOICES = [
    ("AL", _("Alabama")),
    ("AK", _("Alaska")),
    ("AZ", _("Arizona")),
    ("AR", _("Arkansas")),
    ("CA", _("California")),
    ("CO", _("Colorado")),
    ("CT", _("Connecticut")),
    ("DE", _("Delaware")),
    ("FL", _("Florida")),
    ("GA", _("Georgia")),
    ("HI", _("Hawaii")),
    ("ID", _("Idaho")),
    ("IL", _("Illinois")),
    ("IN", _("Indiana")),
    ("IA", _("Iowa")),
    ("KS", _("Kansas")),
    ("KY", _("Kentucky")),
    ("LA", _("Louisiana")),
    ("ME", _("Maine")),
    ("MD", _("Maryland")),
    ("MA", _("Massachusetts")),
    ("MI", _("Michigan")),
    ("MN", _("Minnesota")),
    ("MS", _("Mississippi")),
    ("MO", _("Missouri")),
    ("MT", _("Montana")),
    ("NE", _("Nebraska")),
    ("NV", _("Nevada")),
    ("NH", _("New Hampshire")),
    ("NJ", _("New Jersey")),
    ("NM", _("New Mexico")),
    ("NY", _("New York")),
    ("NC", _("North Carolina")),
    ("ND", _("North Dakota")),
    ("OH", _("Ohio")),
    ("OK", _("Oklahoma")),
    ("OR", _("Oregon")),
    ("PA", _("Pennsylvania")),
    ("RI", _("Rhode Island")),
    ("SC", _("South Carolina")),
    ("SD", _("South Dakota")),
    ("TN", _("Tennessee")),
    ("TX", _("Texas")),
    ("UT", _("Utah")),
    ("VT", _("Vermont")),
    ("VA", _("Virginia")),
    ("WA", _("Washington")),
    ("WV", _("West Virginia")),
    ("WI", _("Wisconsin")),
    ("WY", _("Wyoming")),
]


VEHICLE_TYPE_CHOICES = [
    ('Truck', _('Truck')),
    ('Van', _('Van')),
    ('Car', _('Car')),
    ('SUV', _('SUV')),
    ('Pickup', _('Pickup')),
]

VEHICLE_MAKER_CHOICES = [
    ('Ford', _('Ford')),
    ('Chevrolet', _('Chevrolet')),
    ('Dodge', _('Dodge')),
    ('Toyota', _('Toyota')),
    ('Honda', _('Honda')),
    ('Nissan', _('Nissan')),
    ('Jeep', _('Jeep')),
    ('Mitsubishi', _('Mitsubishi')),
    ('Kia', _('Kia')),
    ('BMW', _('BMW')),
    ('Mercedes-Benz', _('Mercedes-Benz')),
    ('Audi', _('Audi')),
    ('Volkswagen', _('Volkswagen')),
    ('Lexus', _('Lexus')),
    ('Infiniti', _('Infiniti')),
    ('Subaru', _('Subaru')),
    ('GMC', _('GMC')),
    ('Mazda', _('Mazda')),
    ('Pontiac', _('Pontiac')),
    ('Buick', _('Buick')),
    ('Cadillac', _('Cadillac')),
    ('Saturn', _('Saturn')),
    ('GMC', _('GMC')),
    ('Chrysler', _('Chrysler')),
    ('Porsche', _('Porsche')),
    ('Jeep', _('Jeep')),
    ('Maserati', _('Maserati')),
    ('Lotus', _('Lotus')),
    ('Suzuki', _('Suzuki')),
    ('Scion', _('Scion')),
    ('Hummer', _('Hummer')),
    ('Saturn', _('Saturn')),
    ('GMC', _('GMC')),
    ('Chrysler', _('Chrysler')),
    ('Porsche', _('Porsche')),
    ('Jeep', _('Jeep')),
    ('Maserati', _('Maserati')),
    ('Lotus', _('Lotus')),
    ('Suzuki', _('Suzuki')),
    ('Scion', _('Scion')),
    ('Hummer', _('Hummer')),
]
VEHICLE_COLOR_CHOICES = [
    ('Black', _('Black')),
    ('White', _('White')),
    ('Red', _('Red')),
    ('Blue', _('Blue')),
    ('Green', _('Green')),
    ('Yellow', _('Yellow')),
    ('Orange', _('Orange')),
    ('Purple', _('Purple')),
    ('Pink', _('Pink')),
    ('Brown', _('Brown')),
    ('Gray', _('Gray')),
    ('Other', _('Other')),
]

DELIVERY_STATUS_CHOICES = [
    ('Pending', _('Pending')),
    ('In Progress', _('In Progress')),
    ('Delivered', _('Delivered')),
    ('Returned', _('Returned')),
    ('Cancelled', _('Cancelled')),
]