# Inventory Management System

This document provides a comprehensive overview of the inventory management system's structure, functionality, and data models, with special focus on movement operations.

## Core Movement Modules

The inventory system manages stock through three primary movement types:

### 1. Inflows Module
- **Purpose**: Track product entries from suppliers to warehouses
- **Origin**: Supplier entities
- **Destination**: Company warehouses
- **Status Flow**: `pending → approved → completed` (or `rejected`/`cancelled`)
- **Key Validations**: Warehouse capacity checks, supplier relationship verification
- **Property Type**: "Entry"
- **Special Features**: Low stock alerts, automatic quantity updates

### 2. Outflows Module
- **Purpose**: Track product exits from warehouses to customers
- **Origin**: Company warehouses
- **Destination**: Customer entities
- **Status Flow**: `pending → approved → completed` (or `rejected`/`cancelled`)
- **Key Validations**: Stock availability checks, customer relationship verification
- **Special Properties**: Origin/destination address display methods
- **Property Type**: "Exit"
- **Special Features**: Delivery tracking, customer notifications

### 3. Transfers Module
- **Purpose**: Track product movements between company warehouses
- **Origin**: Company warehouse
- **Destination**: Another company warehouse (must be different)
- **Status Flow**: `pending → approved → completed` (or `rejected`/`cancelled`)
- **Key Validations**: Origin-destination difference, dual capacity/availability checks
- **Property Type**: "Transfer"
- **Special Features**: Bidirectional warehouse updates

## Common Architecture

### Models Structure
- **Primary Models** (Inflow/Outflow/Transfer):
  - Track movement metadata and status
  - Link origin and destination entities
  - Store approval/rejection information
  
- **Item Models** (InflowItems/OutflowItems/TransferItems):
  - Link to product entities
  - Store quantity information
  - Support batch operations

### Validation System
- Pre-save validation via signals
- Business rule validation via service classes
- Multi-level integrity checking
- Capacity and availability constraints

### Service Layer
- Transaction-wrapped operations
- Encapsulated business logic
- Permission and access control integration
- Consistent status management

## Real-Time Notification System

Each movement module implements a dedicated notification subsystem:

### Architecture
```
module/notifications/
  ├── constants.py   # Types, titles, and message templates
  ├── handlers.py    # Processing and delivery logic
  └── serializers.py # API data formatting
```

### Notification Types
- Creation notifications
- Status change notifications (approved/rejected)
- Completion notifications
- Special alerts (low stock, capacity warnings)

### Recipient Targeting
- Role-based delivery (managers, stock controllers, warehouse staff)
- Company-scoped notifications
- Real-time WebSocket delivery
- Persistent storage

## Integration Points

- **Warehouse Module**: Tracks total and per-product quantities
- **Product Module**: Maintains overall stock levels
- **Supplier/Customer Modules**: Provide origin/destination entities
- **User Module**: Targets notifications based on roles
- **Notification System**: Delivers real-time updates

## Database Transaction Management

- Atomic operations ensure consistency
- Transaction hooks (`on_commit`) for side effects
- Rollback on validation failures
- Signal-based quantity adjustments

## Best Practices

1. Always use the service layer for operations
2. Validate movements before approval
3. Ensure origin-destination consistency
4. Check capacity and availability constraints
5. Process notifications after transaction commit
6. Target notifications to relevant personnel
7. Maintain audit trails via created_by/updated_by
8. Use proper error handling and logging

## Technical Implementation

- Django signals for reactive processing
- Service classes for business operations
- WebSockets (Django Channels) for real-time communication
- Transaction management for data integrity
- Role-based permission system