# Inventory Management System

This document provides a comprehensive overview of the inventory management system's structure, functionality, and data models.

## System Overview

The inventory system is built around several key concepts:
- Warehouses that store products
- Products with categories and brands
- Movement operations (inflows, outflows, transfers)
- Stock tracking and validation
- Notification system for inventory events
- Load order management
- Supplier management

## Core Data Models

### Base Models
```python
class BaseModel:
    id: UUID
    companie: FK(Companie)
    created_at: datetime
    updated_at: datetime
    created_by: FK(Employeer)
    updated_by: FK(Employeer)

class BaseAddressWithBaseModel(BaseModel):
    phone: str
    email: str
    address: str
    city: str
    state: str
    zip_code: str
    country: str
```

### Warehouse Models
```python
class Warehouse(BaseModel):
    name: str
    limit: int          # Maximum warehouse capacity
    quantity: int       # Current total quantity
    
class WarehouseProduct(BaseModel):
    warehouse: FK(Warehouse)
    product: FK(Product)
    current_quantity: int
```
- Tracks warehouse capacity and current stock levels
- Maintains product-specific quantities
- Validates capacity limits
- Prevents negative quantities

### Product Classification Models

```python
class Brand(BaseModel):
    name: str

class Category(BaseModel):
    name: str

class Product(BaseModel):
    name: str
    description: str
    quantity: int       # Total quantity across all warehouses
    brand: FK(Brand)
    category: FK(Category)
    price: decimal
    min_quantity: int   # Low stock threshold
    max_quantity: int   # Maximum stock threshold

class ProductSku(BaseModel):
    product: FK(Product)
    sku: str
```
- Manages product information and SKUs
- Organizes products by brand and category
- Tracks total quantity across warehouses
- Supports stock level thresholds

### Supplier Model
```python
class Supplier(BaseAddressWithBaseModel):
    name: str
    tax_number: str
    
    @property
    def full_address_display: str
```
- Manages supplier information
- Includes complete address details
- Tracks tax information
- Provides formatted address display

### Movement Models

#### Inflows (Supplier to Warehouse)
```python
class Inflow(BaseModel):
    origin: FK(Supplier)
    destiny: FK(Warehouse)
    status: str        # pending/approved/rejected
    rejection_reason: str

class InflowItems(BaseModel):
    inflow: FK(Inflow)
    product: FK(Product)
    quantity: int
```
- Handles incoming stock from suppliers
- Validates warehouse capacity
- Updates product quantities
- Maintains movement status

#### Outflows (Warehouse to Customer)
```python
class Outflow(BaseModel):
    origin: FK(Warehouse)
    destiny: FK(Customer)
    status: str
    rejection_reason: str

class OutflowItems(BaseModel):
    outflow: FK(Outflow)
    product: FK(Product)
    quantity: int
```
- Manages customer deliveries
- Validates stock availability
- Updates warehouse quantities
- Tracks delivery addresses

#### Transfers (Inter-warehouse)
```python
class Transfer(BaseModel):
    origin: FK(Warehouse)
    destiny: FK(Warehouse)
    status: str
    rejection_reason: str

class TransferItems(BaseModel):
    transfer: FK(Transfer)
    product: FK(Product)
    quantity: int
```
- Handles stock movement between warehouses
- Validates origin and destiny capacities
- Maintains movement status
- Updates quantities in both warehouses

### Load Order Management
```python
class LoadOrder(BaseModel):
    order_number: str      # Auto-generated unique number
    customer: FK(Customer)
    load_to: FK(Vehicle)
    load_date: date

class LoadOrderItem(BaseModel):
    load_order: FK(LoadOrder)
    product: FK(Product)
    quantity: decimal
```
- Manages loading orders for deliveries
- Auto-generates unique order numbers
- Links customers and vehicles
- Tracks product quantities for loading
- Supports atomic order number generation

## Movement Status Flow
All movement types (Inflow, Outflow, Transfer) follow this status flow:
```
pending -> approved/rejected
```
- **Pending**: Initial state for new movements
- **Approved**: Movement completed successfully
- **Rejected**: Movement cancelled with reason

## Signal-Based Validation System

### Pre-save Signals
- Validate warehouse capacity
- Check stock availability
- Prevent negative quantities
- Store previous values for comparison

### Post-save Signals
- Update warehouse quantities
- Update product totals
- Trigger notifications
- Log movement history

### Post-delete Signals
- Restore quantities
- Update warehouse totals
- Clean up related records

## Notification System

Each app includes a notifications package:
```
notifications/
├── constants.py   # Notification types
├── handlers.py    # Event processing
└── serializers.py # Data formatting
```

### Notification Events
- Low stock alerts
- Capacity warnings
- Movement status changes
- Validation failures
- Successful operations

## API Structure

Each app provides REST endpoints for:
- CRUD operations
- Movement processing
- Status updates
- Quantity queries
- Validation checks

## Data Integrity

The system maintains data integrity through:
- Transaction management
- Signal-based validation
- Status tracking
- Audit logging
- Error handling
- Atomic operations for order numbers

## Testing Coverage

Each app includes comprehensive tests for:
- Model validation
- Movement operations
- Capacity checks
- Quantity updates
- Error scenarios
- Order number generation

## Integration Points

The system integrates with:
- Company management
- Customer records
- Supplier management
- Vehicle management
- Employee system
- Notification service

## Best Practices

1. Always use transactions for movements
2. Validate quantities before updates
3. Handle edge cases in signals
4. Maintain audit trails
5. Use status tracking
6. Implement proper error handling
7. Follow notification patterns
8. Use atomic operations for unique identifiers
9. Validate address information
10. Implement proper cascading deletes
