# Missing Modules Implementation Plan

## Overview

This document details the missing modules in the current Django ERP system when compared to the drywall system requirements specified in `requisitos_sistema_drywall_us.md`.

## 1. Sales Management Module

### 1.1 Quotes Module
**Location:** `apps/sales/quotes/`

**Required Functionalities:**
- [ ] Detailed quote creation
- [ ] Product and service inclusion
- [ ] Automatic material calculation by area
- [ ] Discount system
- [ ] Payment terms configuration
- [ ] Delivery and execution deadlines
- [ ] Quote validity
- [ ] Client approval (digital signature)
- [ ] Conversion to order/project

**Required Models:**
- `Quote`
- `QuoteItem`
- `QuoteService`
- `QuoteDiscount`
- `QuoteApproval`

**Estimated Time:** 3-4 weeks

### 1.2 Sales Orders Module
**Location:** `apps/sales/orders/`

**Required Functionalities:**
- [ ] Generation from quotes or directly
- [ ] Automatic inventory reservation
- [ ] Processing status
- [ ] Invoicing
- [ ] Picking
- [ ] Delivery
- [ ] Installation
- [ ] Finalization

**Required Models:**
- `SalesOrder`
- `SalesOrderItem`
- `SalesOrderStatus`
- `InventoryReservation`

**Estimated Time:** 2-3 weeks

### 1.3 Invoicing Module
**Location:** `apps/sales/invoicing/`

**Required Functionalities:**
- [ ] Invoice issuance
- [ ] Integration with tax system
- [ ] Payment processing
- [ ] Receipts
- [ ] Tax control
- [ ] Returns and cancellations

**Required Models:**
- `Invoice`
- `InvoiceItem`
- `Payment`
- `TaxCalculation`
- `Return`

**Estimated Time:** 3-4 weeks

### 1.4 Commissions Management Module
**Location:** `apps/sales/commissions/`

**Required Functionalities:**
- [ ] Commission calculation by seller
- [ ] Sales targets
- [ ] Seller ranking
- [ ] Sales performance reports

**Required Models:**
- `Commission`
- `SalesTarget`
- `SalesPerformance`

**Estimated Time:** 2 weeks

## 2. Financial/Cash Flow Module

### 2.1 Accounts Payable Module
**Location:** `apps/financial/payable/`

**Required Functionalities:**
- [ ] Accounts payable registration
- [ ] Expense categorization
- [ ] Recurring payments
- [ ] Suppliers linked
- [ ] Payment approval
- [ ] Payment methods
- [ ] Receipts (upload)
- [ ] Bank reconciliation
- [ ] Payment reminders

**Required Models:**
- `AccountsPayable`
- `ExpenseCategory`
- `RecurringPayment`
- `PaymentMethod`
- `PaymentVoucher`

**Estimated Time:** 3-4 weeks

### 2.2 Accounts Receivable Module
**Location:** `apps/financial/receivable/`

**Required Functionalities:**
- [ ] Accounts receivable registration
- [ ] Sales/projects binding
- [ ] Installment plans
- [ ] Payment methods
- [ ] Automatic and manual write-off
- [ ] Receipts
- [ ] Delinquency control
- [ ] Payment reminders

**Required Models:**
- `AccountsReceivable`
- `InstallmentPlan`
- `ReceivablePayment`
- `DelinquencyControl`

**Estimated Time:** 3-4 weeks

### 2.3 Cash Flow Module
**Location:** `apps/financial/cashflow/`

**Required Functionalities:**
- [ ] Cash flow projection (daily, weekly, monthly)
- [ ] Bank account balances
- [ ] Account movements
- [ ] Bank reconciliation
- [ ] Management reports
- [ ] Financial dashboard
- [ ] Profitability analysis by project/client

**Required Models:**
- `CashFlowProjection`
- `BankAccount`
- `BankMovement`
- `FinancialReport`

**Estimated Time:** 4-5 weeks

### 2.4 Daily Financial Summary Module
**Location:** `apps/financial/daily_summary/`

**Required Functionalities:**
- [ ] Daily calculation dashboard
- [ ] Total of gross earnings, total costs, net margin
- [ ] Date range filter
- [ ] Detail by job/order
- [ ] Material detail by job
- [ ] Export functionality (CSV/PDF)

**Required Models:**
- `DailySummary`
- `JobCost`
- `MaterialCost`

**Estimated Time:** 2-3 weeks

## 3. Projects Module

### 3.1 Projects Management Module
**Location:** `apps/projects/`

**Required Functionalities:**
- [ ] Project registration
- [ ] Execution schedule
- [ ] Quotes linked
- [ ] Teams allocated
- [ ] Materials used
- [ ] Status tracking
- [ ] Problem registration and solutions
- [ ] Before/after photos
- [ ] Technical documentation

**Required Models:**
- `Project`
- `ProjectTimeline`
- `ProjectTeam`
- `ProjectMaterial`
- `ProjectIssue`
- `ProjectDocument`
- `ProjectPhoto`

**Estimated Time:** 4-5 weeks

## 4. Installation Teams Module

### 4.1 Installation Teams Management Module
**Location:** `apps/installation_teams/`

**Required Functionalities:**
- [ ] Team formation
- [ ] Project allocation
- [ ] Productivity metrics
- [ ] Performance evaluation
- [ ] Project history
- [ ] Commissions (when applicable)
- [ ] Completed trainings

**Required Models:**
- `InstallationTeam`
- `TeamMember`
- `TeamProject`
- `ProductivityMetric`
- `PerformanceEvaluation`
- `TeamTraining`

**Estimated Time:** 3-4 weeks

## Suggested Implementation Timeline

### Phase 1 (8-10 weeks)
1. Sales Management Module (Quotes + Orders)
2. Financial Module (Payable + Receivable)

### Phase 2 (6-8 weeks)
1. Projects Module
2. Installation Teams Module

### Phase 3 (4-6 weeks)
1. Invoicing + Commissions
2. Cash Flow + Daily Summary

## Technical Considerations

### Architectural Standards
- Follow the Service Pattern established in the project
- Implement BaseModel for audit and multi-tenant
- Use atomic transactions
- Implement business validators
- Follow documentation standard with drf-spectacular

### Required Integrations
- Sales Module with Inventory (automatic reservations)
- Financial Module with Sales (billing)
- Projects Module with Teams (allocation)
- Financial Module with Delivery (delivery confirmation)

### Tests
- Implement unit tests for each module
- Integration tests between modules
- Performance tests for reports

## Required Resources

- **Developers:** 2-3 experienced Django developers
- **Total Time:** 18-24 weeks
- **Technical Reviewer:** 1 software architect for review of standards
- **QA:** 1 QA for integration tests

## Risks and Mitigations

### Risks
- Complexity of integrations between modules
- Impact on existing modules
- Performance requirements for financial reports

### Mitigations
- Incremental development with continuous testing
- Frequent code reviews
- Implementation of cache for heavy reports
- Detailed API documentation
