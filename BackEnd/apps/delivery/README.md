# Real-Time Delivery System

This module implements a complete delivery management and real-time tracking system, integrating REST API and WebSockets for bidirectional communications.

## Architecture and Components

### Data Models
- `Delivery`: Main delivery entity with associated customer, driver, vehicle, and load
- `DeliveryCheckpoint`: Historical record of locations and status changes

### Real-Time Communication
- **WebSockets**: Implemented with Django Channels
- **DeliveryConsumer**: Manages connections and authentication
- **Channel Groups**: Separation by delivery_id for specific communication

### Services and Handlers
- `DeliveryHandler`: Encapsulates complex operations with transactional integrity
- `DeliveryValidator`: Business rule validation
- Asynchronous tasks with Celery for notifications and reports

## Real-Time Tracking Flow

1. **Delivery Creation**:
   - Registration of delivery with load, customer, driver, and vehicle
   - Initial status "pending"

2. **Location Updates**:
   - Driver sends GPS location via REST API
   - System validates and stores data
   - Real-time notification via WebSocket
   - Optional ETA updates

3. **Status Transitions**:
   - `pending` → `pickup_in_progress` → `in_transit` → `delivered`
   - Alternatives: `returned` or `failed`
   - Validation of allowed transitions
   - Checkpoint registration for important changes

4. **Monitoring**:
   - Customer tracks delivery in real-time
   - Managers view all company deliveries
   - Complete history recording

## Permission System

- **Drivers**: View and update only their own deliveries
- **Customers**: View only their deliveries
- **Managers**: Full access to company deliveries

## REST API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/deliveries/` | List deliveries |
| POST | `/deliveries/` | Create delivery |
| GET | `/deliveries/{id}/` | Delivery details |
| PUT/PATCH | `/deliveries/{id}/` | Update delivery |
| POST | `/deliveries/{id}/location/` | Update location |
| POST | `/deliveries/{id}/status/` | Update status |
| GET | `/deliveries/{id}/checkpoints/` | List checkpoints |
| GET | `/deliveries/{id}/report/` | Generate report |

## WebSocket

- Connection: `ws://host/ws/delivery/{delivery_id}/`
- Events:
  - `location_update`: New coordinates and ETA
  - `status_update`: Status changes
  - `ping/pong`: Connection maintenance

## Integration with Other Modules

- **Inventory**: LoadOrder for delivery items
- **Companies**: Customer for recipient
- **HR**: Employeer for drivers
- **Vehicles**: Fleet tracking

## Best Practices

- Operations encapsulated in atomic transactions
- Unified JWT authentication
- Robust input validation
- Detailed logging
- OpenAPI/Swagger documentation