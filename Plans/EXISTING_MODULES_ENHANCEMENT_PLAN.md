# Existing Modules Enhancement Plan

## Overview

This document details the necessary improvements for existing modules in the Django ERP that are functional but need to be enhanced to fully meet the drywall system requirements specified in `requisitos_sistema_drywall_us.md`.

## 1. Inventory Module Enhancements

### 1.1 Product Management (apps/inventory/product/)

#### Current State
- Basic product registration
- Categorization and brands
- Price control

#### Required Improvements

##### 1.1.1 Automatic Material Calculation by Area
**Priority:** High

**Required Functionalities:**
- Calculation formulas by product type
- Loss factor configuration
- Automatic calculation based on area (m²/ft²)
- Suggested complementary materials
- Calculation templates by project type

**Required Models:**
```python
# Add to apps/inventory/product/models.py
class ProductCalculationFormula(BaseModel):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    formula_type = models.CharField(max_length=20, choices=[
        ('per_sqft', 'Per Square Foot'),
        ('per_linear_ft', 'Per Linear Foot'),
        ('per_unit', 'Per Unit'),
        ('percentage', 'Percentage of Area')
    ])
    base_quantity = models.DecimalField(max_digits=10, decimal_places=4)
    waste_factor = models.DecimalField(max_digits=5, decimal_places=2, default=0.10)  # 10% default
    minimum_quantity = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
class ProductBundle(BaseModel):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    bundle_type = models.CharField(max_length=30, choices=[
        ('drywall_basic', 'Basic Drywall Package'),
        ('drywall_premium', 'Premium Drywall Package'),
        ('finishing', 'Finishing Package'),
        ('tools', 'Tools Package')
    ])
    
class ProductBundleItem(BaseModel):
    bundle = models.ForeignKey(ProductBundle, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity_per_unit = models.DecimalField(max_digits=10, decimal_places=4)
    is_optional = models.BooleanField(default=False)
```

**Estimated Time:** 2-3 weeks

##### 1.1.2 Technical Specifications
**Priority:** Medium

**Required Functionalities:**
- Technical specifications upload (PDF)
- Structured technical sheets
- Certifications and standards
- Installation instructions
- Product compatibility

**Required Models:**
```python
class ProductSpecification(BaseModel):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    specification_type = models.CharField(max_length=30, choices=[
        ('technical_sheet', 'Technical Sheet'),
        ('installation_guide', 'Installation Guide'),
        ('safety_sheet', 'Safety Data Sheet'),
        ('certification', 'Certification'),
        ('warranty', 'Warranty Information')
    ])
    title = models.CharField(max_length=200)
    content = models.TextField(blank=True)
    file = models.FileField(upload_to='products/specifications/', blank=True)
    
class ProductCompatibility(BaseModel):
    primary_product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='compatible_with')
    compatible_product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='compatible_as')
    compatibility_type = models.CharField(max_length=20, choices=[
        ('recommended', 'Recommended'),
        ('compatible', 'Compatible'),
        ('not_recommended', 'Not Recommended')
    ])
    notes = models.TextField(blank=True)
```

**Estimated Time:** 1-2 weeks

### 1.2 Warehouse Management (apps/inventory/warehouse/)

#### Current State
- Basic warehouse management
- Quantity control
- Basic movements

#### Required Improvements

##### 1.2.1 Physical Inventory and Cyclical Counting
**Priority:** High

**Required Functionalities:**
- Inventory physical planning
- Cyclical counting by category
- Discrepancy registration
- Automatic adjustments
- Accuracy reports

**Required Models:**
```python
# Add to apps/inventory/warehouse/models.py
class PhysicalInventory(BaseModel):
    warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE)
    inventory_type = models.CharField(max_length=20, choices=[
        ('full', 'Full Inventory'),
        ('cycle', 'Cycle Count'),
        ('spot', 'Spot Check')
    ])
    scheduled_date = models.DateField()
    actual_date = models.DateField(null=True)
    status = models.CharField(max_length=20, choices=[
        ('planned', 'Planned'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled')
    ])
    responsible_employee = models.ForeignKey('companies.Employeer', on_delete=models.SET_NULL, null=True)
    
class InventoryCount(BaseModel):
    physical_inventory = models.ForeignKey(PhysicalInventory, on_delete=models.CASCADE)
    product = models.ForeignKey('inventory.Product', on_delete=models.CASCADE)
    system_quantity = models.DecimalField(max_digits=10, decimal_places=2)
    counted_quantity = models.DecimalField(max_digits=10, decimal_places=2)
    discrepancy = models.DecimalField(max_digits=10, decimal_places=2)
    count_date = models.DateTimeField()
    counter_employee = models.ForeignKey('companies.Employeer', on_delete=models.SET_NULL, null=True)
    notes = models.TextField(blank=True)
    
class InventoryAdjustment(BaseModel):
    inventory_count = models.OneToOneField(InventoryCount, on_delete=models.CASCADE)
    adjustment_type = models.CharField(max_length=20, choices=[
        ('increase', 'Increase'),
        ('decrease', 'Decrease')
    ])
    adjustment_quantity = models.DecimalField(max_digits=10, decimal_places=2)
    reason = models.TextField()
    approved_by = models.ForeignKey('companies.Employeer', on_delete=models.SET_NULL, null=True)
    applied_date = models.DateTimeField(null=True)
```

**Estimated Time:** 2-3 weeks

##### 1.2.2 Automatic Replenishment Suggestion
**Priority:** Medium

**Required Functionalities:**
- Replenishment algorithm based on history
- Consideration of seasonality
- Lead time of suppliers
- ABC product analysis
- Automatic alerts

**Required Models:**
```python
class ReplenishmentRule(BaseModel):
    product = models.ForeignKey('inventory.Product', on_delete=models.CASCADE)
    warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE)
    reorder_point = models.DecimalField(max_digits=10, decimal_places=2)
    reorder_quantity = models.DecimalField(max_digits=10, decimal_places=2)
    lead_time_days = models.IntegerField(default=7)
    safety_stock = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
class ReplenishmentSuggestion(BaseModel):
    product = models.ForeignKey('inventory.Product', on_delete=models.CASCADE)
    warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE)
    current_stock = models.DecimalField(max_digits=10, decimal_places=2)
    suggested_quantity = models.DecimalField(max_digits=10, decimal_places=2)
    priority = models.CharField(max_length=10, choices=[
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent')
    ])
    created_date = models.DateTimeField(auto_now_add=True)
    processed = models.BooleanField(default=False)
```

**Estimativa:** 2 semanas

### 1.3 Supplier Management (apps/inventory/supplier/)

#### Current State
- Basic supplier registration
- Contact information

#### Required Improvements

##### 1.3.1 Supplier Evaluation System
**Priority:** Medium

**Required Functionalities:**
- Performance evaluation
- Delivery history
- Product quality
- Compliance with deadlines
- Price evaluation

**Required Models:**
```python
# Add to apps/inventory/supplier/models.py
class SupplierEvaluation(BaseModel):
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE)
    evaluation_period_start = models.DateField()
    evaluation_period_end = models.DateField()
    delivery_performance = models.IntegerField(choices=[(i, i) for i in range(1, 6)])  # 1-5 scale
    quality_rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)])
    price_competitiveness = models.IntegerField(choices=[(i, i) for i in range(1, 6)])
    communication = models.IntegerField(choices=[(i, i) for i in range(1, 6)])
    overall_rating = models.DecimalField(max_digits=3, decimal_places=1)
    comments = models.TextField(blank=True)
    evaluator = models.ForeignKey('companies.Employeer', on_delete=models.SET_NULL, null=True)
    
class SupplierDeliveryHistory(BaseModel):
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE)
    purchase_order = models.ForeignKey('inventory.PurchaseOrder', on_delete=models.CASCADE)
    promised_delivery_date = models.DateField()
    actual_delivery_date = models.DateField(null=True)
    delivery_status = models.CharField(max_length=20, choices=[
        ('on_time', 'On Time'),
        ('early', 'Early'),
        ('late', 'Late'),
        ('partial', 'Partial'),
        ('failed', 'Failed')
    ])
    delay_days = models.IntegerField(default=0)
    delivery_notes = models.TextField(blank=True)
```

**Estimated Time:** 2 weeks

##### 1.3.2 Commercial Terms and Price History
**Priority:** Medium

**Required Functionalities:**
- Payment terms by supplier
- Price history by product
- Contracts and agreements
- Discounts and promotions
- Price variation analysis

**Required Models:**
```python
class SupplierContract(BaseModel):
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE)
    contract_number = models.CharField(max_length=50)
    start_date = models.DateField()
    end_date = models.DateField()
    payment_terms = models.CharField(max_length=50)
    discount_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    contract_file = models.FileField(upload_to='supplier_contracts/', blank=True)
    
class SupplierProductPrice(BaseModel):
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE)
    product = models.ForeignKey('inventory.Product', on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    minimum_quantity = models.DecimalField(max_digits=10, decimal_places=2, default=1)
    valid_from = models.DateField()
    valid_until = models.DateField(null=True)
    currency = models.CharField(max_length=3, default='USD')
```

**Estimated Time:** 1-2 weeks

## 2. Notification System Enhancements (apps/notifications/)

### Current State
- Basic notification system
- Integration with existing modules

### Required Improvements

#### 2.1 Multi-Channel Notifications
**Priority:** High

**Required Functionalities:**
- Email notifications
- SMS notifications
- Push notifications (browser)
- User preferences
- Customizable templates

**Required Models:**
```python
# Add to apps/notifications/models.py
class NotificationChannel(BaseModel):
    name = models.CharField(max_length=50)
    channel_type = models.CharField(max_length=20, choices=[
        ('email', 'Email'),
        ('sms', 'SMS'),
        ('push', 'Push Notification'),
        ('in_app', 'In-App')
    ])
    is_active = models.BooleanField(default=True)
    configuration = models.JSONField(default=dict)  # API keys, endpoints, etc.
    
class UserNotificationPreference(BaseModel):
    user = models.ForeignKey('accounts.User', on_delete=models.CASCADE)
    notification_type = models.CharField(max_length=50)
    email_enabled = models.BooleanField(default=True)
    sms_enabled = models.BooleanField(default=False)
    push_enabled = models.BooleanField(default=True)
    in_app_enabled = models.BooleanField(default=True)
    
class NotificationTemplate(BaseModel):
    name = models.CharField(max_length=100)
    notification_type = models.CharField(max_length=50)
    channel = models.ForeignKey(NotificationChannel, on_delete=models.CASCADE)
    subject_template = models.CharField(max_length=200)
    body_template = models.TextField()
    variables = models.JSONField(default=list)  # Available template variables
```

**Estimated Time:** 2-3 weeks

## 3. Scheduler Module Enhancements (apps/scheduller/)

### Current State
- Basic scheduling system
- Job types

### Required Improvements

#### 3.1 Integration with Projects and Teams
**Priority:** High

**Required Functionalities:**
- Project binding
- Automatic team assignment
- Availability verification
- Conflict resolution
- Automatic notifications

**Required Models:**
```python
# Add to apps/scheduller/models.py
class SchedullerProject(BaseModel):
    scheduller = models.ForeignKey(Scheduller, on_delete=models.CASCADE)
    customer_project = models.ForeignKey('companies.CustomerProject', on_delete=models.CASCADE)
    estimated_duration = models.DurationField()
    actual_duration = models.DurationField(null=True)
    
class SchedullerTeam(BaseModel):
    scheduller = models.ForeignKey(Scheduller, on_delete=models.CASCADE)
    team = models.ForeignKey('companies.WorkTeam', on_delete=models.CASCADE)
    role = models.CharField(max_length=30, choices=[
        ('primary', 'Primary Team'),
        ('support', 'Support Team'),
        ('specialist', 'Specialist Team')
    ])
    
class SchedullerConflict(BaseModel):
    scheduller = models.ForeignKey(Scheduller, on_delete=models.CASCADE)
    conflict_type = models.CharField(max_length=20, choices=[
        ('team_busy', 'Team Not Available'),
        ('vehicle_busy', 'Vehicle Not Available'),
        ('location_conflict', 'Location Conflict'),
        ('time_overlap', 'Time Overlap')
    ])
    conflicting_schedule = models.ForeignKey(Scheduller, on_delete=models.CASCADE, related_name='conflicts')
    resolved = models.BooleanField(default=False)
    resolution_notes = models.TextField(blank=True)
```

**Estimated Time:** 2 weeks

## 4. Vehicle Module Enhancements (apps/vehicle/)

### Current State
- Vehicle registration
- Basic driver assignment

### Required Improvements

#### 4.1 Vehicle Maintenance and Fleet Control
**Priority:** Medium

**Required Functionalities:**
- Maintenance scheduling
- Fuel control
- Repair history
- Periodic inspections
- Expiration alerts

**Required Models:**
```python
# Add to apps/vehicle/models.py
class VehicleMaintenance(BaseModel):
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE)
    maintenance_type = models.CharField(max_length=30, choices=[
        ('oil_change', 'Oil Change'),
        ('tire_rotation', 'Tire Rotation'),
        ('brake_inspection', 'Brake Inspection'),
        ('general_inspection', 'General Inspection'),
        ('repair', 'Repair')
    ])
    scheduled_date = models.DateField()
    completed_date = models.DateField(null=True)
    mileage = models.IntegerField()
    cost = models.DecimalField(max_digits=8, decimal_places=2)
    service_provider = models.CharField(max_length=100)
    notes = models.TextField(blank=True)
    
class VehicleFuelLog(BaseModel):
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE)
    date = models.DateField()
    odometer_reading = models.IntegerField()
    fuel_quantity = models.DecimalField(max_digits=6, decimal_places=2)
    fuel_cost = models.DecimalField(max_digits=8, decimal_places=2)
    fuel_station = models.CharField(max_length=100, blank=True)
    driver = models.ForeignKey('companies.Employeer', on_delete=models.SET_NULL, null=True)
```

**Estimated Time:** 2 weeks

## Suggested Implementation Timeline

### Phase 1 - Critical Functionalities (6-8 weeks)
1. Product Calculation Formulas (2-3 weeks)
2. Physical Inventory System (2-3 weeks)
3. Multi-Channel Notifications (2-3 weeks)

### Phase 2 - Operational Improvements (4-6 weeks)
1. Supplier Evaluation System (2 weeks)
2. Scheduler Enhancements (2 weeks)
3. Replenishment Suggestions (2 weeks)

### Phase 3 - Additional Functionalities (3-4 weeks)
1. Technical Specifications (1-2 weeks)
2. Vehicle Maintenance (2 weeks)
3. Supplier Commercial Terms (1-2 weeks)

## Technical Considerations

### Data Migration
- Complete backup before each migration
- Migration scripts tested in development environment
- Rollback plan for each migration

### Performance
- Database indexes for new queries
- Cache for complex calculations
- Optimization of queries with select_related/prefetch_related

### Integration with Existing Modules
- Maintain compatibility with existing APIs
- API versioning when necessary
- Comprehensive regression tests

## Required Resources

- **Developers:** 2 experienced Django developers
- **Total Time:** 13-18 weeks
- **QA:** 1 QA for regression testing
- **DBA:** For query and index optimization

## Risks and Mitigations

### Risks
- Impact on system performance
- Breaking existing functionality
- Complexity of calculation formulas

### Mitigations
- Incremental development
- Extensive automated tests
- Performance monitoring
- Detailed documentation of changes

## Expected Benefits

- Material calculation automation
- Better inventory control
- Improved communication with clients
- Efficient supplier management
- Reduced operational errors
- Improved user experience