# Partial Modules Enhancement Plan

## Overview

This document details the enhancements needed in the existing modules of the Django ERP to align with the complete requirements of the drywall system specified in `requisitos_sistema_drywall_us.md`.

## 1. Customer Management Module (apps/companies/customers/)

### Current State
- ✅ Basic customer registration
- ✅ Contact and address information
- ✅ Classification fields

### Missing Functionalities

#### 1.1 Project Management by Customer
**Priority:** High

**Required Functionalities:**
- [ ] Association of projects to customers
- [ ] Complete project history
- [ ] Project execution status
- [ ] Project schedule
- [ ] Technical documentation per project
- [ ] Before/after photos per project

**Required Models:**
```python
# Em apps/companies/customers/models.py
class CustomerProject(BaseModel):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    start_date = models.DateField()
    expected_end_date = models.DateField()
    actual_end_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=PROJECT_STATUS_CHOICES)
    project_address = models.TextField()
    
class CustomerProjectDocument(BaseModel):
    project = models.ForeignKey(CustomerProject, on_delete=models.CASCADE)
    document_type = models.CharField(max_length=50)
    file = models.FileField(upload_to='customer_projects/documents/')
    
class CustomerProjectPhoto(BaseModel):
    project = models.ForeignKey(CustomerProject, on_delete=models.CASCADE)
    photo_type = models.CharField(max_length=20, choices=[('before', 'Before'), ('after', 'After'), ('progress', 'Progress')])
    image = models.ImageField(upload_to='customer_projects/photos/')
    description = models.CharField(max_length=200, blank=True)
```

**Estimated Time:** 2-3 weeks

#### 1.2 Business Opportunities and Follow-up
**Priority:** Medium

**Required Functionalities:**
- [ ] Business opportunity registration
- [ ] Follow-up system with reminders
- [ ] Interaction history
- [ ] Lead classification (cold, warm, hot)
- [ ] Satisfaction surveys

**Required Models:**
```python
class BusinessOpportunity(BaseModel):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField()
    estimated_value = models.DecimalField(max_digits=10, decimal_places=2)
    probability = models.IntegerField(choices=[(i, f"{i}%") for i in range(0, 101, 10)])
    expected_close_date = models.DateField()
    status = models.CharField(max_length=20, choices=OPPORTUNITY_STATUS_CHOICES)
    
class CustomerInteraction(BaseModel):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    interaction_type = models.CharField(max_length=20, choices=INTERACTION_TYPE_CHOICES)
    description = models.TextField()
    next_followup = models.DateTimeField(null=True, blank=True)
    
class CustomerSatisfactionSurvey(BaseModel):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    project = models.ForeignKey(CustomerProject, on_delete=models.CASCADE, null=True)
    overall_rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)])
    service_rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)])
    quality_rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)])
    comments = models.TextField(blank=True)
```

**Estimated Time:** 2 weeks

#### 1.3 Improvements in Customer Registration
**Priority:** Medium

**Required Functionalities:**
- [ ] Support for multiple languages (English, Spanish, Portuguese)
- [ ] Fields specific to drywall (construction type, project frequency)
- [ ] Detailed classification system
- [ ] Credit limit and commercial terms
- [ ] Contact person for companies

**Required Modifications:**
```python
# Add to apps/companies/customers/models.py
class Customer(BaseAddressWithBaseModel):
    # Existing fields...
    
    # Novos campos necessários
    preferred_language = models.CharField(max_length=10, choices=LANGUAGE_CHOICES, default='en')
    customer_segment = models.CharField(max_length=50, choices=CUSTOMER_SEGMENT_CHOICES)
    credit_limit = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    payment_terms = models.CharField(max_length=50, choices=PAYMENT_TERMS_CHOICES, default='net_30')
    contact_person_name = models.CharField(max_length=100, blank=True)
    contact_person_phone = models.CharField(max_length=20, blank=True)
    contact_person_email = models.EmailField(blank=True)
    construction_type_preference = models.CharField(max_length=50, choices=CONSTRUCTION_TYPE_CHOICES, blank=True)
    average_project_frequency = models.CharField(max_length=20, choices=FREQUENCY_CHOICES, blank=True)
```

**Estimated Time:** 1 week

## 2. Employee Management Module (apps/companies/employeers/)

### Current State
- ✅ Basic employee registration
- ✅ Personal and professional data
- ✅ Basic attendance control

### Missing Functionalities

#### 2.1 Team System
**Priority:** High

**Required Functionalities:**
- [ ] Team formation
- [ ] Specialization by service type
- [ ] Team leader
- [ ] Member availability
- [ ] Team history by project

**Required Models:**
```python
# Criar apps/companies/teams/models.py
class WorkTeam(BaseModel):
    name = models.CharField(max_length=100)
    team_leader = models.ForeignKey(Employeer, on_delete=models.SET_NULL, null=True, related_name='led_teams')
    specialization = models.CharField(max_length=50, choices=TEAM_SPECIALIZATION_CHOICES)
    is_active = models.BooleanField(default=True)
    max_capacity = models.IntegerField(default=4)
    
class TeamMember(BaseModel):
    team = models.ForeignKey(WorkTeam, on_delete=models.CASCADE)
    employee = models.ForeignKey(Employeer, on_delete=models.CASCADE)
    role_in_team = models.CharField(max_length=30, choices=TEAM_ROLE_CHOICES)
    date_joined = models.DateField(auto_now_add=True)
    date_left = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
```

**Estimated Time:** 2 weeks

#### 2.2 Productivity Metrics
**Priority:** Medium

**Required Functionalities:**
- [ ] Tracking of productivity by employee
- [ ] Metrics by team
- [ ] Performance comparison
- [ ] Individual and team targets
- [ ] Productivity reports

**Required Models:**
```python
class ProductivityMetric(BaseModel):
    employee = models.ForeignKey(Employeer, on_delete=models.CASCADE)
    team = models.ForeignKey(WorkTeam, on_delete=models.CASCADE, null=True)
    metric_date = models.DateField()
    hours_worked = models.DecimalField(max_digits=5, decimal_places=2)
    projects_completed = models.IntegerField(default=0)
    square_feet_completed = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    quality_score = models.DecimalField(max_digits=3, decimal_places=1, null=True)  # 1-10 scale
    efficiency_rating = models.DecimalField(max_digits=3, decimal_places=1, null=True)  # 1-10 scale
    
class ProductivityTarget(BaseModel):
    employee = models.ForeignKey(Employeer, on_delete=models.CASCADE, null=True, blank=True)
    team = models.ForeignKey(WorkTeam, on_delete=models.CASCADE, null=True, blank=True)
    target_period = models.CharField(max_length=20, choices=[('daily', 'Daily'), ('weekly', 'Weekly'), ('monthly', 'Monthly')])
    target_hours = models.DecimalField(max_digits=5, decimal_places=2, null=True)
    target_projects = models.IntegerField(null=True)
    target_square_feet = models.DecimalField(max_digits=10, decimal_places=2, null=True)
```

**Estimated Time:** 2-3 weeks

#### 2.3 Evaluation System
**Priority:** Low

**Required Functionalities:**
- [ ] Periodic performance evaluations
- [ ] Self-evaluation
- [ ] 360-degree feedback
- [ ] Development plans
- [ ] Evaluation history

**Required Models:**
```python
class PerformanceEvaluation(BaseModel):
    employee = models.ForeignKey(Employeer, on_delete=models.CASCADE)
    evaluator = models.ForeignKey(Employeer, on_delete=models.CASCADE, related_name='evaluations_given')
    evaluation_period_start = models.DateField()
    evaluation_period_end = models.DateField()
    technical_skills = models.IntegerField(choices=[(i, i) for i in range(1, 6)])
    teamwork = models.IntegerField(choices=[(i, i) for i in range(1, 6)])
    punctuality = models.IntegerField(choices=[(i, i) for i in range(1, 6)])
    quality_of_work = models.IntegerField(choices=[(i, i) for i in range(1, 6)])
    overall_rating = models.DecimalField(max_digits=3, decimal_places=1)
    comments = models.TextField(blank=True)
    development_plan = models.TextField(blank=True)
```

**Estimated Time:** 2 weeks

## 3. Delivery Management Module (apps/delivery/)

### Current State
- ✅ Basic delivery management
- ✅ Vehicle association

### Missing Functionalities

#### 3.1 Real-time Tracking
**Priority:** High

**Required Functionalities:**
- [ ] Unique tracking link per delivery
- [ ] Automatic notification to client (email/SMS)
- [ ] Interface for client to track delivery
- [ ] Updated estimated arrival time
- [ ] Delivery driver information (name, photo, contact)

**Required Models:**
```python
# Add to apps/delivery/models.py
class DeliveryTracking(BaseModel):
    delivery = models.OneToOneField('Delivery', on_delete=models.CASCADE)
    tracking_code = models.CharField(max_length=50, unique=True)
    current_latitude = models.DecimalField(max_digits=10, decimal_places=8, null=True)
    current_longitude = models.DecimalField(max_digits=11, decimal_places=8, null=True)
    estimated_arrival = models.DateTimeField(null=True)
    last_location_update = models.DateTimeField(null=True)
    
class DeliveryNotification(BaseModel):
    delivery = models.ForeignKey('Delivery', on_delete=models.CASCADE)
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPE_CHOICES)
    recipient_email = models.EmailField(blank=True)
    recipient_phone = models.CharField(max_length=20, blank=True)
    sent_at = models.DateTimeField(null=True)
    delivery_status = models.CharField(max_length=20)
    tracking_link = models.URLField()
    
class DeliveryStatusHistory(BaseModel):
    delivery = models.ForeignKey('Delivery', on_delete=models.CASCADE)
    status = models.CharField(max_length=30)
    timestamp = models.DateTimeField(auto_now_add=True)
    location = models.CharField(max_length=200, blank=True)
    notes = models.TextField(blank=True)
```

**Estimated Time:** 3-4 weeks

#### 3.2 Installation Management
**Priority:** High

**Required Functionalities:**
- [ ] Installation scheduling
- [ ] Installation teams
- [ ] Installation checklist
- [ ] Problem registration
- [ ] Client approval/signature
- [ ] Photos of the finished job

**Required Models:**
```python
class Installation(BaseModel):
    delivery = models.OneToOneField('Delivery', on_delete=models.CASCADE)
    scheduled_date = models.DateTimeField()
    actual_start_time = models.DateTimeField(null=True)
    actual_end_time = models.DateTimeField(null=True)
    installation_team = models.ForeignKey('companies.WorkTeam', on_delete=models.SET_NULL, null=True)
    status = models.CharField(max_length=20, choices=INSTALLATION_STATUS_CHOICES)
    customer_signature = models.TextField(blank=True)  # Base64 encoded signature
    customer_satisfaction_rating = models.IntegerField(null=True, choices=[(i, i) for i in range(1, 6)])
    
class InstallationChecklist(BaseModel):
    installation = models.ForeignKey(Installation, on_delete=models.CASCADE)
    checklist_item = models.CharField(max_length=200)
    is_completed = models.BooleanField(default=False)
    completed_by = models.ForeignKey('companies.Employeer', on_delete=models.SET_NULL, null=True)
    completion_time = models.DateTimeField(null=True)
    notes = models.TextField(blank=True)
    
class InstallationIssue(BaseModel):
    installation = models.ForeignKey(Installation, on_delete=models.CASCADE)
    issue_type = models.CharField(max_length=50, choices=ISSUE_TYPE_CHOICES)
    description = models.TextField()
    severity = models.CharField(max_length=20, choices=SEVERITY_CHOICES)
    resolution = models.TextField(blank=True)
    resolved_by = models.ForeignKey('companies.Employeer', on_delete=models.SET_NULL, null=True)
    resolved_at = models.DateTimeField(null=True)
    
class InstallationPhoto(BaseModel):
    installation = models.ForeignKey(Installation, on_delete=models.CASCADE)
    photo_type = models.CharField(max_length=20, choices=[('before', 'Before'), ('during', 'During'), ('after', 'After')])
    image = models.ImageField(upload_to='installations/photos/')
    description = models.CharField(max_length=200, blank=True)
```

**Estimated Time:** 3-4 weeks

## 4. General Performance and UX Improvements

### 4.1 Enhanced Notification System
**Priority:** Medium

**Required Functionalities:**
- [ ] Real-time push notifications
- [ ] User notification preferences
- [ ] Customizable templates
- [ ] Multiple channels (email, SMS, push)
- [ ] Notification history

**Estimated Time:** 2 weeks

### 4.2 Executive Dashboard
**Priority:** Medium

**Required Functionalities:**
- [ ] Key KPIs in real time
- [ ] Performance charts
- [ ] Automatic alerts
- [ ] Executive reports
- [ ] Period comparison

**Estimated Time:** 2-3 weeks

## Suggested Implementation Timeline

### Phase 1 - High Priority (6-8 weeks)
1. Customer Project Management (2-3 weeks)
2. Employee Teams System (2 weeks)
3. Real-time Delivery Tracking (3-4 weeks)

### Phase 2 - Medium Priority (6-8 weeks)
1. Installation Management (3-4 weeks)
2. Employee Productivity Metrics (2-3 weeks)
3. Business Opportunities & Follow-up (2 weeks)

### Phase 3 - General Improvements (4-5 weeks)
1. Enhanced Notifications (2 weeks)
2. Executive Dashboard (2-3 weeks)
3. Customer Enhancements (1 week)

## Implementation Considerations

### Database Migrations
- Careful planning of migrations to avoid downtime
- Complete backup before major migrations
- Testing in staging environment

### Existing Integrations
- Verify impact on existing integrations
- Update APIs as necessary
- Maintain backward compatibility where possible

### Testing
- Regression tests for existing features
- Performance tests for new features
- Integration tests between modules

## Required Resources

- **Developers:** 2 experienced Django developers
- **Total Time:** 16-21 weeks
- **UX/UI Designer:** For client interfaces and dashboards
- **Tester:** For regression and new feature testing

## Risks

- Impact on existing features
- Changes to established standards
- Performance with increasing data volume
- Complexity of real-time integrations
