from django.utils.translation import gettext

# User Types - Hierarchical Organization
USER_TYPE_CHOICES = (
    ('CEO', gettext('Company CEO')),
    ('Owner', gettext('Company Owner')),
    ('Admin', gettext('System Administrator')),
    ('Manager', gettext('Manager')),
    ('Employee', gettext('Employee')),
    ('Installer', gettext('Installer')),
    ('Stocker', gettext('Stocker')),
    ('Salesman', gettext('Sales man')),
    ('Driver', gettext('Driver')),
    ('Customer', gettext('Customer')),
    ('Supplier', gettext('Supplier')),
)

PROFILE_POSITION_CHOICES = (
    ('Owner', gettext('Owner')),
    ('Director', gettext('Director')),
    ('Manager', gettext('Manager')),
    ('Salesperson', gettext('Salesperson')),
    ('Installer', gettext('Installer')),
    ('Stockist', gettext('Stockist')),
)

PROFILE_DEPARTMENT_CHOICES = (
    ('Executive', gettext('Executive')),
    ('Management', gettext('Management')),
    ('Sales', gettext('Sales')),
    ('Installation', gettext('Installation')),
    ('Warehouse', gettext('Warehouse')),
    ('Administration', gettext('Administration')),
    ('Finance', gettext('Finance')),
    ('HR', gettext('Human Resources')),
)

# HR
PAYROLL_CHOICES = [
    ('Daily', gettext('Daily')),
    ('Weekly', gettext('Weekly')),
    ('Biweekly', gettext('Biweekly')),
    ('Monthly', gettext('Monthly')),
]
PAYMENT_CHOICES = [
    ('Hour', gettext('By Hour')),
]
PAYROLL_STATUS_CHOICES = [
    ('Pending', gettext('Pending')),
    ('Paid', gettext('Paid')),
]

BUSINESS_DAY_CHOICES = [
    (1, gettext('1st Business Day')),
    (2, gettext('2nd Business Day')),
    (3, gettext('3rd Business Day')),
    (4, gettext('4th Business Day')),
    (5, gettext('5th Business Day')),
]

COMPANIE_TYPE_CHOICES = [
    ('Headquarters', gettext('Headquarters')),
    ('Subsidiary', gettext('Subsidiary')),
]

COUNTRY_CHOICES = [
    ('USA', gettext('USA')),
    ('Canada', gettext('Canada')),
    ('Mexico', gettext('Mexico')),
    ('Brazil', gettext('Brazil')),
    ('Argentina', gettext('Argentina')),
    ('Chile', gettext('Chile')),
    ('Colombia', gettext('Colombia')),
    ('Ecuador', gettext('Ecuador')),
    ('Peru', gettext('Peru')),
    ('Paraguay', gettext('Paraguay')),
    ('Other', gettext('Other')),
]

STATE_CHOICES = [
    ("AL", gettext("Alabama")), ("AK", gettext("Alaska")), ("AZ", gettext("Arizona")),
    ("AR", gettext("Arkansas")), ("CA", gettext("California")), ("CO", gettext("Colorado")),
    ("CT", gettext("Connecticut")), ("DE", gettext("Delaware")), ("FL", gettext("Florida")),
    ("GA", gettext("Georgia")), ("HI", gettext("Hawaii")), ("ID", gettext("Idaho")),
    ("IL", gettext("Illinois")), ("IN", gettext("Indiana")), ("IA", gettext("Iowa")),
    ("KS", gettext("Kansas")), ("KY", gettext("Kentucky")), ("LA", gettext("Louisiana")),
    ("ME", gettext("Maine")), ("MD", gettext("Maryland")), ("MA", gettext("Massachusetts")),
    ("MI", gettext("Michigan")), ("MN", gettext("Minnesota")), ("MS", gettext("Mississippi")),
    ("MO", gettext("Missouri")), ("MT", gettext("Montana")), ("NE", gettext("Nebraska")),
    ("NV", gettext("Nevada")), ("NH", gettext("New Hampshire")), ("NJ", gettext("New Jersey")),
    ("NM", gettext("New Mexico")), ("NY", gettext("New York")), ("NC", gettext("North Carolina")),
    ("ND", gettext("North Dakota")), ("OH", gettext("Ohio")), ("OK", gettext("Oklahoma")),
    ("OR", gettext("Oregon")), ("PA", gettext("Pennsylvania")), ("RI", gettext("Rhode Island")),
    ("SC", gettext("South Carolina")), ("SD", gettext("South Dakota")), ("TN", gettext("Tennessee")),
    ("TX", gettext("Texas")), ("UT", gettext("Utah")), ("VT", gettext("Vermont")),
    ("VA", gettext("Virginia")), ("WA", gettext("Washington")), ("WV", gettext("West Virginia")),
    ("WI", gettext("Wisconsin")), ("WY", gettext("Wyoming")),
]

VEHICLE_TYPE_CHOICES = [
    ('Truck', gettext('Truck')), ('Van', gettext('Van')), ('Car', gettext('Car')),
    ('SUV', gettext('SUV')), ('Pickup', gettext('Pickup')),
]

VEHICLE_MAKER_CHOICES = [
    ('Ford', gettext('Ford')), ('Chevrolet', gettext('Chevrolet')), ('Dodge', gettext('Dodge')),
    ('Toyota', gettext('Toyota')), ('Honda', gettext('Honda')), ('Nissan', gettext('Nissan')),
    ('Jeep', gettext('Jeep')), ('BMW', gettext('BMW')), ('Mercedes-Benz', gettext('Mercedes-Benz')),
    ('Audi', gettext('Audi')), ('Volkswagen', gettext('Volkswagen')), ('Lexus', gettext('Lexus')),
    ('Subaru', gettext('Subaru')), ('GMC', gettext('GMC')), ('Mazda', gettext('Mazda')),
    ('Buick', gettext('Buick')), ('Cadillac', gettext('Cadillac')), ('Chrysler', gettext('Chrysler')),
    ('Porsche', gettext('Porsche')), ('Mitsubishi', gettext('Mitsubishi')), ('Kia', gettext('Kia')),
]

VEHICLE_COLOR_CHOICES = [
    ('Black', gettext('Black')), ('White', gettext('White')), ('Red', gettext('Red')),
    ('Blue', gettext('Blue')), ('Green', gettext('Green')), ('Yellow', gettext('Yellow')),
    ('Orange', gettext('Orange')), ('Purple', gettext('Purple')), ('Pink', gettext('Pink')),
    ('Brown', gettext('Brown')), ('Gray', gettext('Gray')), ('Other', gettext('Other')),
]

DELIVERY_STATUS_CHOICES = [
    ('pending', gettext('Pending')),
    ('pickup_in_progress', gettext('Pickup In Progress')),
    ('in_transit', gettext('In Transit')),
    ('delivered', gettext('Delivered')),
    ('returned', gettext('Returned')),
    ('failed', gettext('Failed')),
]

MOVEMENTS_STATUS_CHOICES = [
    ('pending', gettext('Pending')),
    ('approved', gettext('Approved')),
    ('rejected', gettext('Rejected')),
    ('cancelled', gettext('Cancelled')),
    ('completed', gettext('Completed')),
]

PURCHASE_ORDER_STATUS_CHOICES = [
    ('draft', gettext('Draft')),
    ('pending', gettext('Pending')),
    ('approved', gettext('Approved')),
    ('rejected', gettext('Rejected')),
    ('cancelled', gettext('Cancelled')),
    ('completed', gettext('Completed')),
]

LEAD_STATUS_CHOICES = [
    ('new', gettext('New')),
    ('contacted', gettext('Contacted')),
    ('interested', gettext('Interested')),
    ('converted', gettext('Converted')),
    ('rejected', gettext('Rejected')),
]
