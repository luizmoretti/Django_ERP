<div id="top">

<!-- HEADER STYLE: CLASSIC -->
<div align="center">

<img src="django_erp.png" width="30%" style="position: relative; top: 0; right: 0;" alt="Project Logo"/>

# DJANGO_ERP

<em>Transforming Business Operations with Scalable Power</em>

<!-- BADGES -->
<img src="https://img.shields.io/github/license/luizmoretti/Django_ERP?style=flat&logo=opensourceinitiative&logoColor=white&color=0080ff" alt="license">
<img src="https://img.shields.io/github/last-commit/luizmoretti/Django_ERP?style=flat&logo=git&logoColor=white&color=0080ff" alt="last-commit">
<img src="https://img.shields.io/github/languages/top/luizmoretti/Django_ERP?style=flat&color=0080ff" alt="repo-top-language">
<img src="https://img.shields.io/github/languages/count/luizmoretti/Django_ERP?style=flat&color=0080ff" alt="repo-language-count">

<em>Built with the tools and technologies:</em>

<img src="https://img.shields.io/badge/Redis-FF4438.svg?style=flat&logo=Redis&logoColor=white" alt="Redis">
<img src="https://img.shields.io/badge/Cookiecutter-D4AA00.svg?style=flat&logo=Cookiecutter&logoColor=white" alt="Cookiecutter">
<img src="https://img.shields.io/badge/Rich-FAE742.svg?style=flat&logo=Rich&logoColor=black" alt="Rich">
<img src="https://img.shields.io/badge/Ruff-D7FF64.svg?style=flat&logo=Ruff&logoColor=black" alt="Ruff">
<img src="https://img.shields.io/badge/Selenium-43B02A.svg?style=flat&logo=Selenium&logoColor=white" alt="Selenium">
<br>
<img src="https://img.shields.io/badge/Celery-37814A.svg?style=flat&logo=Celery&logoColor=white" alt="Celery">
<img src="https://img.shields.io/badge/Django-092E20.svg?style=flat&logo=Django&logoColor=white" alt="Django">
<img src="https://img.shields.io/badge/Docker-2496ED.svg?style=flat&logo=Docker&logoColor=white" alt="Docker">
<img src="https://img.shields.io/badge/Python-3776AB.svg?style=flat&logo=Python&logoColor=white" alt="Python">
<img src="https://img.shields.io/badge/GitHub%20Actions-2088FF.svg?style=flat&logo=GitHub-Actions&logoColor=white" alt="GitHub%20Actions">
<!-- <img src="https://img.shields.io/badge/Stripe-635BFF.svg?style=flat&logo=Stripe&logoColor=white" alt="Stripe"> -->
<br>
<img src="https://img.shields.io/badge/Next.js-000000.svg?style=flat&logo=Next.js&logoColor=white" alt="Next.js">
<img src="https://img.shields.io/badge/React-61DAFB.svg?style=flat&logo=React&logoColor=black" alt="React">
<img src="https://img.shields.io/badge/TypeScript-3178C6.svg?style=flat&logo=TypeScript&logoColor=white" alt="TypeScript">
<img src="https://img.shields.io/badge/Tailwind_CSS-38B2AC.svg?style=flat&logo=Tailwind-CSS&logoColor=white" alt="Tailwind CSS">
<img src="https://img.shields.io/badge/Axios-5A29E4.svg?style=flat&logo=Axios&logoColor=white" alt="Axios">
<img src="https://img.shields.io/badge/Zod-FF4085.svg?style=flat&logo=Zod&logoColor=white" alt="Zod">

</div>
<br>

---

## 📄 Table of Contents

- [Overview](#-overview)
- [Project Architecture](#-project-architecture)
- [Core Modules](#-core-modules)
- [Frontend Architecture](#-frontend-architecture)
- [Getting Started](#-getting-started)
    - [Prerequisites](#-prerequisites)
    - [Installation](#-installation)
    - [Usage](#-usage)
    - [Testing](#-testing)
- [License](#-license)

---

## ✨ Overview

Django_ERP is a comprehensive enterprise resource planning system designed to streamline and automate complex business operations through a modular, developer-friendly architecture. The core features include:

- 🧩 **Modular Architecture:** Modular design supporting inventory, sales, delivery, and more with clear separation of concerns through Service Pattern implementation.
- 🌐 **API Framework:** Extensive REST API with versioning and consistent serializer patterns, enabling seamless integration across systems.
- ⚡ **Real-time Features:** Real-time updates via WebSocket, ensuring instant communication for delivery tracking and notifications.
- 🔄 **Event System:** Comprehensive signals and event-driven automation using business validators for inventory, purchase orders, and workflows.
- 🛠️ **Multi-tenant Design:** Built-in multi-tenant support through BaseModel with automatic company filtering and user tracking.
- 📚 **Self-documenting API:** Comprehensive OpenAPI schema documentation using drf-spectacular for accelerated development.

---

## 🚀 Getting Started

### 📋 Prerequisites

This project requires the following dependencies:

**Backend:**
- **Programming Language:** Python 3.9+
- **Package Manager:** Pip
- **Container Runtime:** Docker

**Frontend:**
- **Runtime:** Node.js 18+
- **Package Manager:** npm or yarn
- **Modern Browser:** Chrome, Firefox, Safari, or Edge

### ⚙️ Installation

Build Django_ERP from the source and install dependencies:

1. **Clone the repository:**

    ```sh
    ❯ git clone https://github.com/luizmoretti/Django_ERP
    ```

2. **Navigate to the project directory:**

    ```sh
    ❯ cd Django_ERP
    ```

3. **Install the dependencies:**

**Backend - Using [docker](https://www.docker.com/):**

```sh
❯ docker build -t luizmoretti/Django_ERP .
```
**Backend - Using [pip](https://pypi.org/project/pip/):**

```sh
❯ cd BackEnd
❯ pip install -r requirements.txt
```

**Frontend - Using [npm](https://www.npmjs.com/):**

```sh
❯ cd frontend
❯ npm install
```

### 💻 Usage

Run the project with:

**Backend - Using [docker](https://www.docker.com/):**

```sh
docker run -it luizmoretti/Django_ERP
```
**Backend - Using [pip](https://pypi.org/project/pip/):**

```sh
❯ cd BackEnd
❯ python manage.py runserver
```

**Frontend - Using [npm](https://www.npmjs.com/):**

```sh
❯ cd frontend
❯ npm run dev
```

The backend will be available at `http://localhost:8000` and the frontend at `http://localhost:3000`

### 🧪 Testing

Django_ERP supports comprehensive testing for both backend and frontend:

**Backend - Using [docker](https://www.docker.com/):**

```sh
docker exec -it django_erp python manage.py test
```
**Backend - Using [pip](https://pypi.org/project/pip/):**

```sh
❯ cd BackEnd
❯ pytest
```

**Frontend - Using [npm](https://www.npmjs.com/):**

```sh
❯ cd frontend
❯ npm run lint
❯ npm run build  # Validates TypeScript compilation
```

## 🏗️ Project Architecture

Django_ERP implements a well-structured, layered architecture based on modern software design principles:

### Service Pattern

The system implements a comprehensive Service Pattern with clear separation of responsibilities:

- **Services/Handlers:** Encapsulate business logic in atomic transactions
- **Services/Validators:** Implement business rules and validation logic
- **Services/Reports:** Generate specialized domain reports

### Model Hierarchy

- **BaseModel:** Foundation for all models with:
  - UUID primary keys for distribution-friendly identifiers
  - Multi-tenant support via company field
  - Automatic audit fields (created_at, updated_at, created_by, updated_by)
  - Automated company inheritance for data isolation

- **BaseAddressWithBaseModel:** Extension with standardized address and contact fields

### API Architecture

- **Serializers:** Consistent pattern with read/write field separation
- **Views:** Hierarchical structure with base classes for common behavior
- **Permissions:** Granular permission system with company-aware filtering

---

## 🧩 Core Modules

### Inventory Management

- **Warehouses:** Management of storage locations with capacity tracking
- **Inflows:** Product entries from suppliers to warehouses
- **Transfers:** Internal movement between warehouses
- **Outflows:** Product exits from warehouses to customers

### Human Resources

- **Employees:** Complete employee management with position hierarchy
- **Attendance:** Time tracking with support for hourly and daily payment
- **Payroll:** Automated payroll calculation based on attendance

### Vehicle Fleet

- **Vehicles:** Comprehensive vehicle management with assignment tracking
- **Drivers:** Assignment and qualification management
- **Tracking:** Vehicle usage and availability monitoring

### User Management

- **Accounts:** Custom user model with email-based authentication
- **Profiles:** Extended user profiles with role-based permissions
- **Multi-tenant:** Company-based data isolation throughout the system

### Frontend Application

- **Next.js Architecture:** Modern React application with App Router and TypeScript
- **Authentication:** JWT-based secure authentication with automatic token refresh
- **UI Components:** Comprehensive component library with Tailwind CSS styling
- **State Management:** Context-based state management with type-safe reducers
- **Form Handling:** Robust form validation using React Hook Form and Zod schemas

---

## 🖥️ Frontend Architecture

Django_ERP features a modern, type-safe frontend built with Next.js 15 and cutting-edge web technologies, providing an intuitive user experience for complex ERP operations.

### Technology Stack

- **Framework:** Next.js 15 with App Router for modern React development
- **Language:** TypeScript for type safety and developer experience  
- **Styling:** Tailwind CSS v4 for utility-first responsive design
- **State Management:** React Context with useReducer for predictable state updates
- **Form Validation:** React Hook Form with Zod schemas for robust data validation
- **HTTP Client:** Axios with automatic token management and request/response interceptors
- **Icons:** Lucide React for consistent, customizable iconography

### Authentication System

The frontend implements a comprehensive authentication system with enterprise-grade security:

- **JWT Token Management:** Secure token storage with automatic refresh capabilities
- **Role-Based Access Control:** Hierarchical user types from CEO to Customer with granular permissions
- **Protected Routes:** Server-side and client-side route protection using Next.js middleware
- **Password Security:** Advanced password validation with strength indicators
- **Session Management:** Secure token storage in httpOnly cookies and sessionStorage

### Component Architecture

- **Atomic Design:** Hierarchical component structure from basic UI elements to complex pages
- **Type Safety:** Full TypeScript coverage with strict type checking
- **Accessibility:** WCAG-compliant components with proper ARIA labels
- **Responsive Design:** Mobile-first approach with breakpoint-aware layouts
- **Error Boundaries:** Graceful error handling with user-friendly fallbacks

### API Integration

- **RESTful Integration:** Seamless connection with Django REST Framework backend
- **Request Interceptors:** Automatic authentication token injection and CSRF protection
- **Error Handling:** Centralized error transformation and user notification system
- **Loading States:** Comprehensive loading indicators and skeleton screens
- **Retry Logic:** Automatic retry for failed requests with exponential backoff

### Performance Features

- **Code Splitting:** Automatic route-based code splitting for optimal loading
- **Static Generation:** Pre-rendered pages where applicable for improved SEO
- **Optimized Bundling:** Tree shaking and dead code elimination
- **Caching Strategy:** Intelligent caching of API responses and static assets
- **Progressive Enhancement:** Core functionality works without JavaScript

---

## 📜 License

Django_erp is protected under the [LICENSE](http://www.apache.org/licenses/) License. For more details, refer to the [LICENSE](/LICENSE) file.

---

<div align="left"><a href="#top">⬆ Return</a></div>

---
