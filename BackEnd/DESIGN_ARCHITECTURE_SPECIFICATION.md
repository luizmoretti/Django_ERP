# Design Architecture Specification (D.A.S)
## Companies Management System

### 1. System Overview
#### 1.1 Purpose
Enterprise management system specialized for Drywall sector companies, offering inventory management, human resources, and business administration functionalities.

#### 1.2 Technical Stack
- **Backend Framework**: Django 5.2 + Django REST Framework 3.16.0
- **Database**: PostgreSQL 3.2.6
- **Cache**: Redis 5.2.1
- **Task Queue**: Celery 5.5.1
- **Channels**: Django Channels 4.2.2 + Daphne 4.1.2
- **Authentication**: JWT (djangorestframework-simplejwt 5.5.0)
- **API Documentation**: DRF Spectacular 0.28.0
- **Payment Processing**: Stripe 12.0.0
- **File Handling**: Pillow 11.2.1
- **Security**: Django-Axes 7.0.2 (proteção contra força bruta)
- **Maps Integration**: Google Maps API 4.10.0
- **Testing**: Factory Boy 3.3.3, Faker 37.1.0

### 2. System Architecture

#### 2.1 Core Components
```
DryWallWareHouse/
├── api/                    # API endpoints centralization
├── apps/                   # Main application modules
│   ├── accounts/          # User management and authentication
│   │   ├── management/    # Custom management commands
│   │   └── notifications/ # User-related notifications
│   │
│   ├── companies/         # Company and HR management
│   │   ├── attendance/    # Employee attendance tracking
│   │   ├── customers/     # Customer relationship management
│   │   ├── employeers/    # Employee management
│   │   └── notifications/ # Company-related notifications
│   │
│   ├── deliveries/        # Delivery management and tracking
│   │   ├── vehicles/      # Vehicle fleet management
│   │   └── notifications/ # Delivery-related notifications
│   │
│   ├── inventory/         # Stock and product management
│   │   ├── brand/        # Product brand management
│   │   ├── categories/   # Product categorization
│   │   ├── inflows/      # Stock receiving management
│   │   ├── load_order/   # Loading order management
│   │   ├── outflows/     # Stock dispatch management
│   │   ├── product/      # Product catalog management
│   │   ├── purchase_order/ # Purchase order processing
│   │   ├── supplier/     # Supplier management
│   │   ├── transfer/     # Stock transfer between warehouses
│   │   └── warehouse/    # Warehouse management
│   │
│   └── notifications/     # Centralized notification system
│       ├── base.py       # Base notification handler
│       ├── consumers.py  # WebSocket consumers
│       ├── middleware.py # Notification middleware
│       ├── routing.py    # WebSocket routing
│       └── utils.py      # Notification utilities
├── core/                  # Project settings and configurations
├── static/                # Static files
├── media/                 # User-uploaded files
└── logs/                  # System logs
```

#### 2.2 Module Structure
Each app module follows the structure:
```
module_name/
├── models.py             # Data models and database structure
├── serializers.py        # API serializers for data transformation
├── views.py             # API views and request handling
├── urls.py              # Module routing and endpoint definitions
├── permissions.py       # Custom permissions and access control
├── filters.py           # Query filters and search parameters
├── services/           # Business logic layer
│   ├── handlers.py     # Core business operations
│   └── validators.py   # Business rule validations
├── notifications/       # Notification handlers
│   ├── constants.py    # Notification constants and templates
│   └── handlers.py     # Notification logic and delivery
└── tests/              # Module tests
    ├── test_models.py     # Model tests
    ├── test_services.py   # Business logic tests
    ├── test_views.py      # API endpoint tests
    └── test_permissions.py # Permission tests
```

### 3. Design Patterns & Standards

#### 3.1 Service Pattern
- **Separação de Responsabilidades**:
  - **Views**: Gerenciamento de requisições e respostas HTTP
  - **Services**: Encapsulamento da lógica de negócio
  - **Validators**: Validação de regras de negócio
  - **Serializers**: Transformação e validação de dados

- **Estrutura de Services**:
  ```python
  class XxxService:
      def __init__(self):
          self.validator = XxxBusinessValidator()
          
      def create_xxx(self, data, user):
          # Validação de regras de negócio
          self.validator.validate_company_access(data, user)
          
          # Operações em transação atômica
          with transaction.atomic():
              # Implementação...
              
          return instance
  ```

#### 3.2 API Design
- **URL Structure**: `/api/v1/{app_name}/{resource}/`
- **HTTP Methods**:
  - GET: List/Retrieve
  - POST: Create
  - PUT/PATCH: Update
  - DELETE: Remove
- **Response Format**:
  ```json
  {
    "status": "success|error",
    "data": {},
    "message": "string",
    "errors": []
  }
  ```

- **Documentação com drf-spectacular**:
  ```python
  @extend_schema_view(
      get=extend_schema(
          tags=['Módulo - Submódulo'],
          operation_id='operation_name',
          summary='Descrição da operação',
          responses={200: XxxSerializer}
      )
  )
  ```

#### 3.2 Authentication & Authorization
- JWT-based authentication
- Token refresh mechanism
- Role-based access control
- Custom permission classes per view
- Company-specific access control

#### 3.3 Database Design
- Use of UUID for primary keys
- Audit fields (created_at, updated_at, created_by, updated_by)
- Proper indexing strategy
- Foreign key constraints
- Company-based data segregation

### 4. Module Specifications

#### 4.1 Accounts Module
- Custom user model (NormalUser)
- Authentication endpoints
- User profile management
- Permission management
- Role-based access control

#### 4.2 Companies Module
- Company profile management
- HR management
- Department organization
- Employee records
- Payroll processing
- Company-specific settings

#### 4.3 Inventory Module
- Product management
- Stock control
- Order processing
- Supplier management
- Inventory tracking
- Purchase order system
- Warehouse management

### 5. Security Standards

#### 5.1 Authentication Security
- JWT token expiration: Access (1 hour), Refresh (7 days)
- Password hashing using Django's default hasher
- Rate limiting on authentication endpoints
- Company-based access restrictions

#### 5.2 Data Security
- CORS configuration
- Input validation
- XSS protection
- SQL injection prevention
- File upload validation
- Data segregation by company

### 6. Performance Optimization

#### 6.1 Caching Strategy
- Redis cache implementation
- Cache invalidation rules
- Cached endpoints listing
- Company-specific cache keys
- Transaction-aware caching

#### 6.2 Database Optimization
- Query optimization
- Proper indexing
- Bulk operations
- Select_related and prefetch_related usage
- Company-filtered querysets

### 7. Error Handling

#### 7.1 Exception Handling
- Custom exception classes
- Standardized error responses
- Logging levels:
  - ERROR: System errors
  - WARNING: Business rule violations
  - INFO: Important operations
  - DEBUG: Development information

#### 7.2 Logging
- Centralized logging
- Log rotation
- Error tracking
- Performance monitoring
- Company context in logs

### 8. Testing Strategy

#### 8.1 Test Types
- Unit tests
- Integration tests
- API tests
- Performance tests
- Permission tests
- Company isolation tests

#### 8.2 Test Coverage
- Minimum coverage: 80%
- Critical paths: 100%
- Authentication flows
- Business logic
- Permission scenarios

### 9. Documentation Standards

#### 9.1 Code Documentation
- Docstrings for all classes and methods
- Type hints
- Clear variable naming
- Comments for complex logic
- Language: English (US)

#### 9.2 API Documentation
- OpenAPI/Swagger documentation
- Endpoint descriptions
- Request/Response examples
- Authentication details
- Permission requirements

### 10. Deployment & DevOps

#### 10.1 Environment Configuration
- Development
- Staging
- Production
- Environment variables
- Company-specific configurations

#### 10.2 Monitoring
- System health checks
- Performance metrics
- Error tracking
- User activity monitoring
- Company usage analytics

### 11. Maintenance & Updates

#### 11.1 Code Maintenance
- Regular dependency updates
- Security patches
- Performance optimization
- Technical debt management
- Backward compatibility

#### 11.2 Database Maintenance
- Regular backups
- Data archiving
- Index optimization
- Query performance monitoring
- Company data isolation

### 12. Notification System

#### 12.1 Structure
- Base notification handler (BaseNotificationHandler)
- App-specific implementations
- Standardized message templates
- Role-based recipient targeting
- Company-specific notifications

#### 12.2 Implementation
- Transaction-based notification timing
- Atomic operations
- Cache-aware updates
- Company-specific filtering
- Recipient type management

#### 12.3 Permission System
- Role-based access control:
  - Owner & CEO: Full access
  - Admin: Full access to assigned company
  - Manager: Department-level access
  - Stocker: Limited inventory access
  - Employee: View-only access
- Custom model permissions
- Company-specific access
- Hierarchical permission structure

#### 12.4 Purchase Order System
- Approval workflow
- Status management (pending, approved, rejected, cancelled)
- Item management
- Price tracking
- Supplier integration
- Notification triggers
- Permission requirements:
  - Approval permissions
  - Item management permissions
  - View permissions

### 13. Delivery System

#### 13.1 Vehicle Management
- Fleet registration and tracking
- Vehicle maintenance scheduling
- Driver assignment
- Route optimization
- Fuel consumption tracking

#### 13.2 Delivery Workflow
- Order assignment
- Route planning
- Real-time tracking
- Delivery confirmation
- Customer signature capture
- Proof of delivery documentation

#### 13.3 Integration Points
- Inventory system for stock updates
- Purchase order system for delivery scheduling
- Customer notification system
- GPS tracking integration
- Mobile app integration for drivers

### 14. WebSocket Implementation

#### 14.1 Real-time Features
- Live notifications
- Delivery tracking updates
- Stock level alerts
- Order status changes
- User presence tracking

#### 14.2 WebSocket Architecture
- Channel layers with Redis
- Consumer implementation
- Authentication middleware
- Message routing
- Connection management

#### 14.3 Security Measures
- Authentication token validation
- Company-specific channels
- Rate limiting
- Connection pooling
- Error handling

### 15. Mobile Integration

#### 15.1 Mobile API Endpoints
- Dedicated mobile API routes
- Optimized payload size
- Cached responses
- Offline capabilities
- Push notification support

#### 15.2 Mobile Features
- Delivery driver app
- Customer order tracking
- Warehouse management
- Inventory scanning
- Digital signature capture

#### 15.3 Security & Performance
- Mobile-specific authentication
- Request compression
- Image optimization
- Bandwidth management
- Battery usage optimization

### 16. Third-party Integrations

#### 16.1 Payment Processing
- Stripe integration details
- Payment workflow
- Webhook handling
- Error recovery
- Refund processing

#### 16.2 External Services
- Email service providers
- SMS gateways
- Maps and geocoding services
- Analytics platforms
- External APIs

#### 16.3 Integration Security
- API key management
- Webhook authentication
- Rate limiting
- Error handling
- Audit logging

---

## Versioning
- Version: 1.0
- Last Updated: 2025-04-18
- Status: Active

## Contact
For technical questions or clarifications about this specification, please contact the development team.