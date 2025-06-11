# Requirements Document for Drywall Company Management System

## Table of Contents

1. [Introduction](#introduction)
2. [System Requirements](#system-requirements)
3. [Database Schema](#database-schema)
4. [System Architecture](#system-architecture)
5. [Interface Mockups](#interface-mockups)
6. [Estimated Timeline](#estimated-timeline)
7. [Final Considerations](#final-considerations)

## Introduction

This document presents the requirements for the development of a comprehensive management system for a company specializing in Drywall. The system should cover all company operations, from product and inventory management to financial control and human resources.

### System Objective

Develop an integrated solution that allows efficient management of all aspects of the Drywall company, optimizing processes, reducing operational errors, and providing accurate management information for decision making.

### Proposed Technologies

- **Backend**: Django + Django REST Framework
- **Frontend**: React + TypeScript
- **Database**: PostgreSQL (recommended for robustness and compatibility with Django)
- **Non-Database**: Redis (for caching, session management, background tasks and notifications)
- **Authentication**: JWT (JSON Web Tokens)
- **Containerization**: Docker (optional, to facilitate deployment)

## System Requirements

### 1. Product and Warehouse Management

#### 1.1 Product Registration

- Complete product registration with:
  - Unique code
  - Name
  - Detailed description
  - Category (boards, profiles, screws, compounds, tools, etc.)
  - Manufacturer/Supplier
  - Barcode
  - Product photos
  - Technical specification (PDF upload)
  - Cost price
  - Profit margin
  - Sale price
  - Minimum stock
  - Maximum stock
  - Warehouse location (aisle, shelf, position)
  - Status (active/inactive)

#### 1.2 Inventory Management

- Real-time inventory control
- Multiple warehouses
- Tracking of inventory movements (inflows, outflows, transfers)
- Complete history of movements by product
- Low stock alerts
- Automatic replenishment suggestion
- Physical inventory with cycle counting support
- Inventory adjustments with reason and responsible party recording
- Reports of discrepancies between physical inventory and system

#### 1.3 Inventory Movement Control

- **Product Entries**:
  - Detailed recording of all product entries into inventory
  - Linking with supplier invoices
  - Automatic and real-time updating of available quantity in inventory
  - Recording of destination warehouse
  - Recording of date, time, and person responsible for entry
  - Possibility of partial entry (when supplier delivery is partial)
  - Verification of received products (quantity, quality, specifications)
  - Recording of discrepancies between order and receipt
  - Automatic generation of alerts in case of discrepancies

- **Product Outflows**:
  - Detailed recording of all product outflows from inventory
  - Linking with sales orders, internal requisitions, or adjustments
  - Automatic and real-time updating of available quantity in inventory
  - Recording of source warehouse
  - Recording of date, time, and person responsible for outflow
  - Blocking outflows when inventory is insufficient (with override possibility by authorized user)
  - Inventory reservation for orders in process
  - Automatic inventory reduction upon delivery confirmation
  - Return handling with inventory update

- **Transfers Between Warehouses**:
  - Detailed recording of product transfers between warehouses
  - Two-step process: outflow from source warehouse and inflow to destination warehouse
  - Automatic and real-time updating of quantities in both warehouses
  - Transfer status (requested, in transit, received, canceled)
  - Recording of date, time, and persons responsible for outflow and inflow
  - Receipt confirmation with possibility of recording discrepancies
  - Tracking of products in transit
  - Complete history of transfers by product and by warehouse

- **Movement Dashboard**:
  - Graphical visualization of inventory movements
  - Filters by period, product, movement type, and warehouse
  - Performance indicators (inventory turnover, average time in stock)
  - Alerts for products without movement for configurable period
  - Movement reports exportable in various formats

- **Integrations**:
  - Automatic integration with purchasing module for entries
  - Automatic integration with sales module for outflows
  - Integration with financial module for inventory valuation
  - Integration with logistics module for transfer planning

#### 1.4 Supplier Management

- Complete supplier registration
- Purchase history by supplier
- Supplier evaluation
- Average delivery times
- Commercial terms
- Contacts

#### 1.5 Purchasing and Replenishment

- Automatic generation of purchase orders based on minimum stock
- Purchase approval workflow
- Tracking of open orders
- Receipt of goods with verification
- Recording of incoming invoices
- Payment term control
- Price history by product/supplier

### 2. Customer Management

#### 2.1 Customer Registration

- Complete registration data (individuals and businesses)
  - Name/Business Name
  - SSN/EIN/ITIN
  - Complete address
  - Preferred Language (English, Spanish, Portuguese(Brazil), etc.)
  - Contacts (phone, mobile, email)
  - Contact person (for businesses)
  - Segment (construction, renovations, etc.)
  - Classification (VIP, regular, occasional)
  - Registration date
  - Credit limit
  - Specific commercial terms
  - Notes

#### 2.2 History and Relationship

- Complete purchase history
- Payment history
- Completed projects
- Interactions (contact records, complaints, requests)
- Business opportunities
- Follow-up reminders
- Satisfaction surveys

#### 2.3 Project Management

- Project registration
- Execution timeline
- Linked quotes
- Allocated teams
- Materials used
- Status tracking
- Problem and solution recording
- Before/after photos
- Technical documentation

### 3. Employee Management

#### 3.1 Employee Registration

- Complete personal data
- Documentation (SSN, Driver's License, etc.)
- Address
- Emergency contacts
- Position/Role
- Department
- Hire date
- Salary
- Benefits
- Skills and certifications
- Photo

#### 3.2 Time and Attendance Control

- Time clock (check-in/check-out)
- Overtime
- Absences and justifications
- Late arrivals
- Time bank
- Vacation (scheduling and control)
- Leaves of absence

#### 3.3 Teams and Productivity

- Formation of installation teams
- Project allocation
- Productivity metrics
- Performance evaluation
- History of completed projects
- Commissions (when applicable)
- Completed training

#### 3.4 Payroll (Integration)

- Salary calculation
- Advances
- Commissions
- Deductions
- Benefits
- Taxes
- Receipt generation
- Integration with accounting system

### 4. Cash Flow Management

#### 4.1 Accounts Payable

- Accounts payable registration
- Expense categorization
- Recurring payments
- Linked suppliers
- Payment approval
- Payment methods
- Receipts (upload)
- Bank reconciliation
- Due date alerts

#### 4.2 Accounts Receivable

- Accounts receivable registration
- Linking with sales/projects
- Installment plans
- Receipt methods
- Automatic and manual clearing
- Receipts
- Delinquency control
- Automatic collection notifications

#### 4.3 Cash Flow

- Cash flow projection (daily, weekly, monthly)
- Bank balances
- Movements between accounts
- Bank reconciliation
- Management reports
- Financial dashboard
- Profitability analysis by project/customer

#### 4.4 Financial Reports

- Simplified income statement
- Cost analysis
- Contribution margin by product/service
- Profitability by customer/project
- Revenue and expense evolution
- Period comparisons
- Charts and indicators

#### 4.5 Daily Financial Summary (Based on PDF Analysis)

- **Daily Calculation Dashboard/Report**:
  - Display total gross earnings, total costs (material costs + other tracked costs), and total net margin for a selected day.
  - Ability to filter by date range.
- **Job/Order Breakdown**:
  - List all jobs/orders completed or delivered on the selected day.
  - For each job/order, display:
    - Customer/Project Name
    - Delivery Address
    - Total Revenue (Sum of Sell Price * Quantity for all items)
    - Total Material Cost (Sum of Buy Price * Quantity for all items)
    - Total Margin (Total Revenue - Total Material Cost)
    - Optional: Fields for tracking other costs associated with the job (e.g., Fixed Costs, Variable Costs, Commissions)- **Material Detail per Job**:
  - Within each job/order, list all materials sold/used.
  - For each material:
    - Product Name
    - Buy Price (Cost) - *Should be editable by the user for specific job adjustments*
    - Sell Price - *Should be editable by the user for specific job adjustments*
    - Quantity
    - Margin per Unit (Sell Price - Buy Price)
    - Total Margin for Line Item (Margin per Unit * Quantity)
- **Data Integration**:
  - Automatically pull data from Sales Orders, Product Costs, and Deliveries modules.
  - Ensure real-time updates as deliveries are confirmed and costs are updated.
- **Export Functionality**:
  - Ability to export the daily summary and detailed breakdown in formats like CSV or PDF.

### 5. Sales Management

#### 5.1 Quotes

- Creation of detailed quotes
- Inclusion of products and services
- Automatic calculation of materials by area
- Discounts
- Payment terms
- Delivery and execution deadlines
- Validity
- Customer approval (digital signature)
- Conversion to order/project

#### 5.2 Sales Orders

- Generation from quotes or direct
- Automatic inventory reservation
- Processing status
- Invoicing
- Picking
- Delivery
- Installation
- Completion

#### 5.3 Invoicing

- Invoice issuance (integration with tax system)
- Payment processing
- Receipts
- Tax control
- Returns and cancellations

#### 5.4 Commission Management

- Calculation of commissions by salesperson
- Sales targets
- Salesperson ranking
- Sales performance reports

### 6. Delivery and Installation Management

#### 6.1 Delivery Logistics

- Delivery routing
- Scheduling
- Available vehicles
- Drivers
- Load capacity
- Delivery confirmation (digital signature)
- Incident recording
- Real-time tracking

#### 6.1.1 Customer Delivery Tracking

- Automatic generation of unique link for each delivery
- Sending tracking link to customer via email and SMS when delivery is generated
- Interface for customer to track delivery location in real time
- Constantly updated estimated time of arrival
- Delivery person information (name, photo, and contact)
- Details of items being delivered
- Delivery status history

#### 6.1.2 Delivery Completion Process

- Mandatory photographic record by delivery person showing where all products were placed
- Multiple photos can be attached to adequately document the delivery
- Collection of customer's digital signature directly on the delivery person's device
- In case of failure to collect signature with the delivery person:
  - Automatic generation of link for remote digital signature
  - Sending link to customer via email and SMS
  - Reminder notifications if signature is not completed within 24 hours
  - Dashboard for tracking deliveries pending signature

#### 6.1.3 Delivery Rating System

- Automatic sending of rating link after delivery confirmation
- 1 to 5 star rating system (5 being the maximum rating)
- Fields for comments and additional feedback
- Ability to attach photos in case of problems
- Notification to managers for ratings below 4 stars
- Dashboard with customer satisfaction metrics
- Performance reports by delivery person, region, and period

#### 6.2 Installation Teams

- Installation scheduling
- Team allocation
- Necessary tools
- Complementary materials
- Installation checklist
- Photographic record (before/during/after)
- Customer acceptance form signature

#### 6.3 Quality Control

- Post-installation inspection
- Non-conformity recording
- Corrective actions
- Satisfaction survey
- Service warranty

## Non-Functional Requirements

### 1. Usability

- Intuitive and responsive interface
- Adaptation for mobile devices (tablets for external teams)
- Fast response times
- Contextual help
- Integrated tutorials

### 2. Security

- Secure authentication (JWT)
- Role-based access control
- Recording of all operations (logs)
- Automatic backup
- Encryption of sensitive data
- Compliance with data protection regulations (CCPA, GDPR)

### 3. Performance

- Maximum response time of 2 seconds for common operations
- Support for multiple simultaneous users
- Optimization for variable internet connections (for external teams)

### 4. Scalability

- Architecture that allows growth of data volume
- Possibility of adding new modules
- Support for multiple branches/units

### 5. Integrations

- RESTful API for external integrations
- Integration with tax systems
- Integration with accounting systems
- Integration with payment gateways
- Possibility of integration with e-commerce

## Database Schema

The database schema was designed using Django ORM as the basis for modeling. Below are the main entities and their relationships:

### Product and Warehouse Module

- **Category**: Hierarchical product classification
- **UnitOfMeasure**: Units of measure for products (unit, ft, sq ft, lb, etc.)
- **Manufacturer**: Product manufacturers
- **Supplier**: Product suppliers with complete data
- **Warehouse**: Company warehouses/storage facilities
- **InventoryLocation**: Positions within warehouses (aisle, shelf, position)
- **Product**: Complete product registration with all information
- **ProductImage**: Images associated with products
- **ProductSupplier**: Relationship between products and suppliers
- **Inventory**: Quantity control by product and warehouse
- **InventoryMovement**: Record of all inventory movements
- **PhysicalInventory**: Control of physical inventories
- **InventoryItem**: Items counted in each inventory

### Customer Module

- **Customer**: Complete customer registration (individuals/businesses)
- **DeliveryAddress**: Additional delivery addresses
- **CustomerInteraction**: Record of contacts, complaints, requests
- **Project**: Projects completed for customers
- **ProjectImage**: Before/during/after images of projects
- **ProjectTeam**: Employees allocated to each project

### Employee Module

- **Department**: Company sectors
- **Position**: Functions within the company
- **Employee**: Complete employee registration
- **Skill**: Technical competencies
- **EmployeeSkill**: Skills of each employee
- **TimeRecord**: Time and attendance control
- **Vacation**: Vacation scheduling and control

### Cash Flow Module

- **BankAccount**: Company bank accounts
- **FinancialCategory**: Categorization of revenues and expenses
- **AccountsPayable**: Financial obligations
- **AccountsReceivable**: Financial rights
- **BankMovement**: Record of all financial movements
- **Note**: The Daily Financial Summary (section 4.5) is primarily generated by querying and aggregating data from the Sales Module (Orders, OrderItems) and potentially JobCost entities for a specific date range, rather than requiring dedicated tables within the Cash Flow module itself. However, the results of these daily summaries can inform overall cash flow analysis.

### Sales Module

- **PaymentTerm**: Payment forms and conditions
- **Quote**: Commercial proposals for customers
- **QuoteItem**: Items included in each quote (linking to Product, storing quantity, proposed price)
- **Order**: Confirmed sales orders (linking to Customer, Project, etc.)
- **OrderItem**: Items included in each confirmed order. Links to `Order` and `Product`. Stores:
  - `quantity`: Quantity ordered.
  - `unit_sell_price`: Actual selling price per unit for this item in this order (editable, defaults from Product).
  - `unit_buy_price`: Actual cost price per unit for this item relevant to this order (editable, defaults from Product).
- **JobCost** (Optional): Tracks additional costs associated with an order/job. Links to `Order`. Stores:
  - `cost_type`: Type of cost (e.g., Fixed, Variable, Commission, Labor).
  - `description`: Details of the cost.
  - `amount`: Monetary value of the cost.

### Delivery and Installation Module

- **Vehicle**: Delivery fleet
- **Delivery**: Delivery scheduling and control
- **DeliveryOrder**: Relationship between deliveries and orders
- **DeliveryItem**: Items delivered in each delivery
- **Installation**: Installation scheduling and control
- **InstallationImage**: Photos of the installation process
- **InstallationChecklist**: Installation verification items

### User and Permission Module

- **Profile**: System access profiles
- **UserProfile**: Assignment of profiles to users

## System Architecture

The system architecture follows the modern web application pattern, with clear separation between frontend and backend, communicating through RESTful APIs.

### Main Components

#### 1. Frontend (Client)

- **Technologies**: React, TypeScript, Redux, Material-UI
- **Responsibilities**:
  - Responsive user interface
  - Application state management
  - Client-side form validation
  - Communication with backend via REST API
  - Authentication and session management
  - Report and dashboard visualization

#### 2. Backend (Server)

- **Technologies**: Django, Django REST Framework, PostgreSQL
- **Responsibilities**:
  - Business logic implementation
  - RESTful API exposure
  - Authentication and authorization
  - Data validation
  - Data persistence
  - Report generation
  - Integration with external systems

#### 3. Database

- **Technology**: PostgreSQL
- **Responsibilities**:
  - Persistent data storage
  - Referential integrity
  - Backup and recovery
  - Complex and optimized queries

### Architecture Diagram

```
+----------------------------------+
|                                  |
|  Client (Browser/Mobile App)     |
|                                  |
+----------------+----------------+
                 |
                 | HTTPS/REST API
                 |
+----------------v----------------+
|                                  |
|     Web Server (Nginx/uWSGI)     |
|                                  |
+----------------+----------------+
                 |
                 |
+----------------v----------------+
|                                  |
|   Django Application (Backend)   |
|                                  |
|  +----------------------------+  |
|  |                            |  |
|  |  Django REST Framework     |  |
|  |  (API Layer)               |  |
|  |                            |  |
|  +----------------------------+  |
|                                  |
|  +----------------------------+  |
|  |                            |  |
|  |  Django Apps (Modules)     |  |
|  |  - Products/Warehouses     |  |
|  |  - Customers               |  |
|  |  - Employees               |  |
|  |  - Cash Flow               |  |
|  |  - Sales                   |  |
|  |  - Deliveries/Installation |  |
|  |                            |  |
|  +----------------------------+  |
|                                  |
|  +----------------------------+  |
|  |                            |  |
|  |  Django ORM                |  |
|  |  (Data Access Layer)       |  |
|  |                            |  |
|  +----------------------------+  |
|                                  |
+----------------+----------------+
                 |
                 |
+----------------v----------------+
|                                  |
|      PostgreSQL Database         |
|                                  |
+----------------------------------+
        |              |
        |              |
+-------v------+ +-----v----------+
|              | |                |
| File Storage | | Email Service  |
|              | |                |
+--------------+ +----------------+
```

### Security

- Authentication via JWT with token expiration
- Automatic token renewal
- Role-based access control
- Protection against CSRF (Cross-Site Request Forgery)
- Encryption of sensitive data
- Input data validation
- Protection against SQL injection
- Output data sanitization
- HTTPS for all communications
- Firewalls and network access control
- Regular backups
- Security monitoring

### Scalability and Performance

- Stateless architecture to facilitate horizontal scalability
- Caching of frequently accessed data
- Database query optimization
- Result pagination
- Lazy loading of frontend components
- Asset minimization and bundling
- HTTP response compression
- Adequate database indexing

## Interface Mockups

The interface mockups were developed to illustrate the structure and functionalities of the main system screens. Below are some examples:

### 1. Main Dashboard

The main dashboard provides an overview of the system with:
- Side menu with access to all modules
- Cards with summary information (monthly sales, day's deliveries, low stock, accounts payable)
- Recent activities section
- List of ongoing projects with status

### 2. Product Management

#### 2.1 Product List
- Advanced search and filters
- Table with main information
- Quick actions (edit, view, disable)
- Pagination

#### 2.2 Product Registration/Editing
- Form organized in sections (basic information, dimensions, inventory, prices)
- Image and document upload
- Real-time validation

### 3. Customer Management

#### 3.1 Customer Registration
- Adaptive form for individuals or businesses
- Multiple addresses
- Commercial terms
- Notes

#### 3.2 Customer View
- Organized tabs (data, projects, financial, history)
- Activity summary
- Quick actions

### 4. Sales Management

#### 4.1 Quote Creation
- Customer selection
- Addition of products and services
- Automatic value calculation
- Payment terms
- Notes

#### 4.2 Order View
- Current status with update option
- Organized tabs (data, items, deliveries, payments)
- Delivery and installation schedule

### 5. Delivery Management

#### 5.1 Delivery and Installation Schedule
- Integrated calendar view (day, week, month) for scheduling both deliveries and installations
- Ability to create and manage delivery and installation appointments directly from the calendar
- Color-coded events to distinguish between deliveries and installations
- Details of the day's deliveries and installations
- Quick actions (confirm, reschedule, cancel)
- Drag-and-drop functionality for easy rescheduling
- Resource allocation view to prevent scheduling conflicts

#### 5.2 Delivery Confirmation
- Item checklist
- Recipient registration
- Photo and signature capture
- Notes

### 6. Financial Management

#### 6.1 Financial Dashboard
- Summary of revenues and expenses
- Cash flow chart
- Accounts receivable and payable
- Bank balances

#### 6.2 Payment Registration
- Accounts payable selection
- Payment data (date, amount, interest, penalty, discount)
- Payment method
- Receipt upload

### 7. Inventory Movement Control

#### 7.1 Product Entry Registration
- Supplier and invoice selection
- Product list with quantities and values
- Destination warehouse selection
- Verification with purchase order
- Discrepancy recording

#### 7.2 Product Output Registration
- Linking with sales order
- Product list with quantities
- Source warehouse selection
- Availability confirmation
- Picking document generation

#### 7.3 Transfer Between Warehouses
- Selection of source and destination warehouses
- Product list with quantities
- Transfer status
- Sending and receiving confirmation
- Transfer tracking

#### 7.4 Movement Query
- Filters by period, product, type, and warehouse
- Detailed view of each movement
- Inventory evolution charts
- Report export

## Estimated Timeline

The system development has been divided into phases to allow incremental deliveries:

- **Phase 1 (2-3 months)**: Product, Warehouse, and Customer Modules
- **Phase 2 (2-3 months)**: Sales and Delivery Modules
- **Phase 3 (2-3 months)**: Employee and Cash Flow Modules
- **Phase 4 (1-2 months)**: Integrations, final adjustments, and complete implementation

## Final Considerations

This document presents a complete view of the requirements for the Drywall company management system. During development, it is recommended to hold periodic meetings for validation and adjustment of requirements, ensuring that the system fully meets the business needs.

The modular development will allow incremental delivery of functionalities, enabling partial use of the system while new modules are implemented.

The choice of technologies (Django + Django REST Framework for the backend and React + TypeScript for the frontend) provides a solid and modern foundation for development, focusing on security, performance, and scalability.

The interface mockups and database schema provide a clear view of the system structure and operation, serving as a guide for development.

It is recommended that development follow agile methodologies, with incremental deliveries and constant validations, to ensure quality and adherence to business requirements.
