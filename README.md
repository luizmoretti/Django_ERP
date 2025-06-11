<div id="top">

<!-- HEADER STYLE: CLASSIC -->
<div align="center">

<img src="Django_ERP.png" width="30%" style="position: relative; top: 0; right: 0;" alt="Project Logo"/>

# DJANGO_ERP

<em>Transforming Business Operations with Scalable Power</em>

<!-- BADGES -->
<img src="https://img.shields.io/github/license/luizmoretti/Django_ERP?style=flat&logo=opensourceinitiative&logoColor=white&color=0080ff" alt="license">
<img src="https://img.shields.io/github/last-commit/luizmoretti/Django_ERP?style=flat&logo=git&logoColor=white&color=0080ff" alt="last-commit">
<img src="https://img.shields.io/github/languages/top/luizmoretti/Django_ERP?style=flat&color=0080ff" alt="repo-top-language">
<img src="https://img.shields.io/github/languages/count/luizmoretti/Django_ERP?style=flat&color=0080ff" alt="repo-language-count">

<em>Built with the tools and technologies:</em>

<img src="https://img.shields.io/badge/Markdown-000000.svg?style=flat&logo=Markdown&logoColor=white" alt="Markdown">
<img src="https://img.shields.io/badge/Redis-FF4438.svg?style=flat&logo=Redis&logoColor=white" alt="Redis">
<!-- <img src="https://img.shields.io/badge/Cookiecutter-D4AA00.svg?style=flat&logo=Cookiecutter&logoColor=white" alt="Cookiecutter"> -->
<!-- <img src="https://img.shields.io/badge/Rich-FAE742.svg?style=flat&logo=Rich&logoColor=black" alt="Rich"> -->
<!-- <img src="https://img.shields.io/badge/Ruff-D7FF64.svg?style=flat&logo=Ruff&logoColor=black" alt="Ruff"> -->
<img src="https://img.shields.io/badge/Selenium-43B02A.svg?style=flat&logo=Selenium&logoColor=white" alt="Selenium">
<br>
<img src="https://img.shields.io/badge/Celery-37814A.svg?style=flat&logo=Celery&logoColor=white" alt="Celery">
<img src="https://img.shields.io/badge/Django-092E20.svg?style=flat&logo=Django&logoColor=white" alt="Django">
<img src="https://img.shields.io/badge/Docker-2496ED.svg?style=flat&logo=Docker&logoColor=white" alt="Docker">
<img src="https://img.shields.io/badge/Python-3776AB.svg?style=flat&logo=Python&logoColor=white" alt="Python">
<img src="https://img.shields.io/badge/GitHub%20Actions-2088FF.svg?style=flat&logo=GitHub-Actions&logoColor=white" alt="GitHub%20Actions">
<img src="https://img.shields.io/badge/Stripe-635BFF.svg?style=flat&logo=Stripe&logoColor=white" alt="Stripe">

</div>
<br>

---

## 📄 Table of Contents

- [Overview](#-overview)
- [Getting Started](#-getting-started)
    - [Prerequisites](#-prerequisites)
    - [Installation](#-installation)
    - [Usage](#-usage)
    - [Testing](#-testing)
- [Features](#-features)
- [Project Structure](#-project-structure)
    - [Project Index](#-project-index)
- [Roadmap](#-roadmap)
- [License](#-license)
- [Acknowledgment](#-acknowledgment)

---

## ✨ Overview

Django_ERP is a comprehensive enterprise resource planning system built on Django, designed to streamline complex business operations with modular, scalable components. The core features include:

- 🧩 **Modular Architecture:** Extensive source code summaries across inventory, sales, HR, notifications, and more, enabling flexible customization.
- 🌐 **Real-Time Communication:** WebSocket consumers and routing facilitate live updates for delivery, notifications, and system events.
- ⚙️ **Automation & Scheduling:** Background tasks, signals, and scheduled reports automate routine workflows, ensuring operational efficiency.
- 🔒 **Robust API:** Well-structured serializers, viewsets, and URL routing support seamless integration and data management.
- 🧪 **Testing & Validation:** Dedicated test cases and validators maintain high code quality and system reliability.
- 🛠️ **Separation of Concerns:** Clear app boundaries and service layers promote maintainability and scalability.

---

## 📌 Features

|      | Component          | Details                                                                                     |
| :--- | :----------------- | :------------------------------------------------------------------------------------------ |
| ⚙️  | **Architecture**   | <ul><li>Modular Django project with apps for core functionalities</li><li>Uses REST API architecture via Django REST Framework</li><li>Containerized with Docker, orchestrated via docker-compose</li></ul> |
| 🔩 | **Code Quality**   | <ul><li>Follows PEP8 standards</li><li>Uses type hints and docstrings</li><li>Includes code linters (e.g., ruff) in CI/CD</li></ul> |
| 📄 | **Documentation**  | <ul><li>Provides README with setup instructions</li><li>Includes Docker and deployment configs</li><li>Has `.env.example` for environment variables</li></ul> |
| 🔌 | **Integrations**    | <ul><li>CI/CD via GitHub Actions (`.github/workflows/django.yml`)</li><li>Containerization with Docker and Docker Compose</li><li>Web server Nginx (`nginx.conf`) for reverse proxy</li><li>External services: Redis, PostgreSQL, Celery</li></ul> |
| 🧩 | **Modularity**      | <ul><li>Separated Django apps for different modules (e.g., auth, sales, inventory)</li><li>Uses Django signals and custom apps for extensibility</li></ul> |
| 🧪 | **Testing**         | <ul><li>Includes unit tests and integration tests</li><li>Uses pytest and Django test framework</li><li>Test coverage integrated into CI/CD pipeline</li></ul> |
| ⚡️  | **Performance**     | <ul><li>Uses Redis for caching and Celery for background tasks</li><li>Optimized database queries with select_related/prefetch_related</li><li>Configured for scalable deployment with Docker</li></ul> |
| 🛡️ | **Security**        | <ul><li>Uses Django security middleware (CSRF, X-Content-Type-Options)</li><li>JWT authentication via `djangorestframework_simplejwt`</li><li>Environment variables for sensitive configs</li></ul> |
| 📦 | **Dependencies**    | <ul><li>Major dependencies include Django, DRF, Celery, Redis, PostgreSQL</li><li>Uses `requirements.txt` for dependency management</li><li>Includes development tools like `pytest`, `ruff`, `factory_boy`</li></ul> |

---

## 📁 Project Structure

```sh
└── Django_ERP/
    ├── .github
    │   └── workflows
    ├── BackEnd
    │   ├── .env.example
    │   ├── .gitattributes
    │   ├── .gitignore
    │   ├── DESIGN_ARCHITECTURE_SPECIFICATION.md
    │   ├── DRF Docs
    │   ├── Dockerfile
    │   ├── LICENSE
    │   ├── api
    │   ├── apps
    │   ├── basemodels
    │   ├── core
    │   ├── custom_settings
    │   ├── docker-compose.yml
    │   ├── manage.py
    │   ├── nginx
    │   ├── requirements.txt
    │   ├── static
    │   └── templates
    ├── FrontEnd
    │   └── .gitignore
    ├── Plans
    │   ├── EXECUTIVE_SUMMARY_ANALYSIS.md
    │   ├── EXISTING_MODULES_ENHANCEMENT_PLAN.md
    │   ├── MISSING_MODULES_PLAN.md
    │   └── PARTIAL_MODULES_ENHANCEMENT_PLAN.md
    └── SysRequirements
        └── requisitos_sistema_drywall_us.md
```

---

### 📑 Project Index

<details open>
	<summary><b><code>DJANGO_ERP/</code></b></summary>
	<!-- __root__ Submodule -->
	<!-- <details> -->
		<!-- <summary><b>__root__</b></summary> -->
		<!-- <blockquote>
			<div class='directory-path' style='padding: 8px 0; color: #666;'>
				<code><b>⦿ __root__</b></code>
			<table style='width: 100%; border-collapse: collapse;'>
			<thead>
				<tr style='background-color: #f8f9fa;'>
					<th style='width: 30%; text-align: left; padding: 8px;'>File Name</th>
					<th style='text-align: left; padding: 8px;'>Summary</th>
				</tr>
			</thead>
			</table>
		</blockquote> -->
	<!-- </details> -->
	<!-- SysRequirements Submodule -->
	<details>
		<summary><b>SysRequirements</b></summary>
		<blockquote>
			<div class='directory-path' style='padding: 8px 0; color: #666;'>
				<code><b>⦿ SysRequirements</b></code>
			<table style='width: 100%; border-collapse: collapse;'>
			<thead>
				<tr style='background-color: #f8f9fa;'>
					<th style='width: 30%; text-align: left; padding: 8px;'>File Name</th>
					<th style='text-align: left; padding: 8px;'>Summary</th>
				</tr>
			</thead>
				<tr style='border-bottom: 1px solid #eee;'>
					<td style='padding: 8px;'><b><a href='https://github.com/luizmoretti/Django_ERP/blob/master/SysRequirements/requisitos_sistema_drywall_us.md'>requisitos_sistema_drywall_us.md</a></b></td>
					<td style='padding: 8px;'>- This code file, <code>requisitos_sistema_drywall_us.md</code>, serves as the foundational requirements document for the Drywall Company Management System<br>- It outlines the core objectives and scope of the project, emphasizing the development of an integrated platform that streamlines operations across inventory, financials, and human resources<br>- By defining the systems needs and architecture, this document guides the overall design and implementation, ensuring that the resulting application effectively supports comprehensive management and decision-making for the drywall business.</td>
				</tr>
			</table>
		</blockquote>
	</details>
	<!-- Plans Submodule -->
	<details>
		<summary><b>Plans</b></summary>
		<blockquote>
			<div class='directory-path' style='padding: 8px 0; color: #666;'>
				<code><b>⦿ Plans</b></code>
			<table style='width: 100%; border-collapse: collapse;'>
			<thead>
				<tr style='background-color: #f8f9fa;'>
					<th style='width: 30%; text-align: left; padding: 8px;'>File Name</th>
					<th style='text-align: left; padding: 8px;'>Summary</th>
				</tr>
			</thead>
				<tr style='border-bottom: 1px solid #eee;'>
					<td style='padding: 8px;'><b><a href='https://github.com/luizmoretti/Django_ERP/blob/master/Plans/EXECUTIVE_SUMMARY_ANALYSIS.md'>EXECUTIVE_SUMMARY_ANALYSIS.md</a></b></td>
					<td style='padding: 8px;'>- Provides a comprehensive executive summary analyzing the current Django ERP system against drywall business requirements<br>- Highlights core modules implemented, critical gaps in sales and financial management, and outlines phased development strategies<br>- Serves as a strategic roadmap for prioritizing features, estimating resources, and mitigating risks to guide the system’s evolution toward a complete, scalable drywall enterprise solution.</td>
				</tr>
				<tr style='border-bottom: 1px solid #eee;'>
					<td style='padding: 8px;'><b><a href='https://github.com/luizmoretti/Django_ERP/blob/master/Plans/MISSING_MODULES_PLAN.md'>MISSING_MODULES_PLAN.md</a></b></td>
					<td style='padding: 8px;'>- Provides a comprehensive plan for implementing missing modules in the Django ERP system, aligning functionalities across sales, financial, projects, and installation teams<br>- Serves as a strategic roadmap to bridge gaps between current capabilities and system requirements, ensuring structured development, integration, and deployment of essential features to support business operations and scalability.</td>
				</tr>
				<tr style='border-bottom: 1px solid #eee;'>
					<td style='padding: 8px;'><b><a href='https://github.com/luizmoretti/Django_ERP/blob/master/Plans/PARTIAL_MODULES_ENHANCEMENT_PLAN.md'>PARTIAL_MODULES_ENHANCEMENT_PLAN.md</a></b></td>
					<td style='padding: 8px;'>- Defines the roadmap for enhancing and expanding core modules of the Django ERP system, focusing on customer project management, employee team structures, delivery tracking, and installation workflows<br>- Facilitates systematic development aligned with project priorities, ensuring comprehensive functionality, improved user experience, and seamless integration across modules to support business growth and operational efficiency.</td>
				</tr>
				<tr style='border-bottom: 1px solid #eee;'>
					<td style='padding: 8px;'><b><a href='https://github.com/luizmoretti/Django_ERP/blob/master/Plans/EXISTING_MODULES_ENHANCEMENT_PLAN.md'>EXISTING_MODULES_ENHANCEMENT_PLAN.md</a></b></td>
					<td style='padding: 8px;'>- This code file serves as a foundational blueprint for enhancing the product management capabilities within the Django ERP system<br>- Its primary purpose is to define the data models necessary for implementing automated material calculations based on project area measurements<br>- These enhancements aim to streamline inventory planning by enabling dynamic, formula-driven estimations of material requirements, thereby improving accuracy and efficiency in project execution<br>- Overall, it supports the systems goal of providing a comprehensive, adaptable inventory module aligned with drywall project specifications.</td>
				</tr>
			</table>
		</blockquote>
	</details>
	<!-- BackEnd Submodule -->
	<details>
		<summary><b>BackEnd</b></summary>
		<blockquote>
			<div class='directory-path' style='padding: 8px 0; color: #666;'>
				<code><b>⦿ BackEnd</b></code>
			<table style='width: 100%; border-collapse: collapse;'>
			<thead>
				<tr style='background-color: #f8f9fa;'>
					<th style='width: 30%; text-align: left; padding: 8px;'>File Name</th>
					<th style='text-align: left; padding: 8px;'>Summary</th>
				</tr>
			</thead>
				<tr style='border-bottom: 1px solid #eee;'>
					<td style='padding: 8px;'><b><a href='https://github.com/luizmoretti/Django_ERP/blob/master/BackEnd/manage.py'>manage.py</a></b></td>
					<td style='padding: 8px;'>- Facilitates execution of core administrative commands for managing the Django-based backend, enabling tasks such as database migrations, server startup, and application management within the overall architecture<br>- Acts as the entry point for command-line interactions, ensuring seamless integration and operational control of the backend services.</td>
				</tr>
				<tr style='border-bottom: 1px solid #eee;'>
					<td style='padding: 8px;'><b><a href='https://github.com/luizmoretti/Django_ERP/blob/master/BackEnd/docker-compose.yml'>docker-compose.yml</a></b></td>
					<td style='padding: 8px;'>- Defines the containerized architecture for deploying a Django-based web application, orchestrating services such as the web server, database, cache, task queue, and reverse proxy<br>- Facilitates seamless startup, health monitoring, and inter-service dependencies, ensuring a scalable, maintainable, and resilient environment for development and production workflows.</td>
				</tr>
				<tr style='border-bottom: 1px solid #eee;'>
					<td style='padding: 8px;'><b><a href='https://github.com/luizmoretti/Django_ERP/blob/master/BackEnd/Dockerfile'>Dockerfile</a></b></td>
					<td style='padding: 8px;'>- Sets up the container environment for a Python-based web application, ensuring necessary dependencies and system tools are installed<br>- Configures the application to run using Daphne on port 8000, facilitating asynchronous communication<br>- Integrates project requirements and prepares static/media directories, supporting deployment within a Dockerized architecture for scalable, production-ready operation.</td>
				</tr>
				<tr style='border-bottom: 1px solid #eee;'>
					<td style='padding: 8px;'><b><a href='https://github.com/luizmoretti/Django_ERP/blob/master/BackEnd/LICENSE'>LICENSE</a></b></td>
					<td style='padding: 8px;'>- Defines licensing terms for the project, ensuring legal clarity and open-source distribution rights<br>- It establishes the permissions granted to users and contributors, supporting the projects goal of widespread accessibility and collaboration within the overall architecture<br>- This license underpins the open-source nature of the entire codebase, facilitating community engagement and reuse.</td>
				</tr>
				<tr style='border-bottom: 1px solid #eee;'>
					<td style='padding: 8px;'><b><a href='https://github.com/luizmoretti/Django_ERP/blob/master/BackEnd/DESIGN_ARCHITECTURE_SPECIFICATION.md'>DESIGN_ARCHITECTURE_SPECIFICATION.md</a></b></td>
					<td style='padding: 8px;'>- Defines the core architecture and standards for the Companies Management System, facilitating seamless integration of inventory, HR, delivery, and notification modules within a Django-based enterprise platform<br>- Ensures consistent API design, security, and performance practices, supporting scalable, company-specific operations and real-time communication across diverse business functionalities.</td>
				</tr>
				<tr style='border-bottom: 1px solid #eee;'>
					<td style='padding: 8px;'><b><a href='https://github.com/luizmoretti/Django_ERP/blob/master/BackEnd/requirements.txt'>requirements.txt</a></b></td>
					<td style='padding: 8px;'>- Defines the core dependencies and environment setup for the backend, supporting features like asynchronous communication, REST API endpoints, real-time WebSocket interactions, and background task processing<br>- Ensures consistent package management across development and deployment, facilitating scalable, secure, and maintainable architecture within a Django-based microservices ecosystem.</td>
				</tr>
				<tr style='border-bottom: 1px solid #eee;'>
					<td style='padding: 8px;'><b><a href='https://github.com/luizmoretti/Django_ERP/blob/master/BackEnd/.env.example'>.env.example</a></b></td>
					<td style='padding: 8px;'>- Defines environment variables for configuring core backend services, including database, cache, email, security, and optional integrations<br>- Facilitates seamless setup and deployment of the Django-based ERP system by centralizing configuration parameters, ensuring consistency across development, testing, and production environments<br>- Supports scalable, secure, and maintainable architecture aligned with the overall project structure.</td>
				</tr>
			</table>
			<!-- apps Submodule -->
			<details>
				<summary><b>apps</b></summary>
				<blockquote>
					<div class='directory-path' style='padding: 8px 0; color: #666;'>
						<code><b>⦿ BackEnd.apps</b></code>
					<table style='width: 100%; border-collapse: collapse;'>
					<thead>
						<tr style='background-color: #f8f9fa;'>
							<th style='width: 30%; text-align: left; padding: 8px;'>File Name</th>
							<th style='text-align: left; padding: 8px;'>Summary</th>
						</tr>
					</thead>
						<tr style='border-bottom: 1px solid #eee;'>
							<td style='padding: 8px;'><b><a href='https://github.com/luizmoretti/Django_ERP/blob/master/BackEnd/apps/apps.py'>apps.py</a></b></td>
							<td style='padding: 8px;'>- Defines the configuration for the core application module within the Django project, establishing the applications identity and default primary key type<br>- It integrates the app into the overall architecture, enabling Django to recognize and manage the apps components effectively<br>- This setup facilitates organized app registration and consistent database modeling across the project.</td>
						</tr>
					</table>
					<!-- notifications Submodule -->
					<details>
						<summary><b>notifications</b></summary>
						<blockquote>
							<div class='directory-path' style='padding: 8px 0; color: #666;'>
								<code><b>⦿ BackEnd.apps.notifications</b></code>
							<table style='width: 100%; border-collapse: collapse;'>
							<thead>
								<tr style='background-color: #f8f9fa;'>
									<th style='width: 30%; text-align: left; padding: 8px;'>File Name</th>
									<th style='text-align: left; padding: 8px;'>Summary</th>
								</tr>
							</thead>
								<tr style='border-bottom: 1px solid #eee;'>
									<td style='padding: 8px;'><b><a href='https://github.com/luizmoretti/Django_ERP/blob/master/BackEnd/apps/notifications/tests.py'>tests.py</a></b></td>
									<td style='padding: 8px;'>- Provides test cases for the notifications module within the backend application, ensuring the functionality and reliability of notification-related features<br>- Supports maintaining code quality and robustness by validating notification behaviors, which are integral to user engagement and system responsiveness across the overall architecture.</td>
								</tr>
								<tr style='border-bottom: 1px solid #eee;'>
									<td style='padding: 8px;'><b><a href='https://github.com/luizmoretti/Django_ERP/blob/master/BackEnd/apps/notifications/consumers.py'>consumers.py</a></b></td>
									<td style='padding: 8px;'>- Facilitates real-time user notifications through WebSocket connections by authenticating users via JWT tokens, managing group memberships, and delivering structured notification messages based on severity levels<br>- Integrates seamlessly into the backend architecture to ensure secure, immediate communication of alerts and updates tailored to individual users within the system.</td>
								</tr>
								<tr style='border-bottom: 1px solid #eee;'>
									<td style='padding: 8px;'><b><a href='https://github.com/luizmoretti/Django_ERP/blob/master/BackEnd/apps/notifications/views.py'>views.py</a></b></td>
									<td style='padding: 8px;'>- Defines the notification-related endpoints within the backend architecture, facilitating the handling and delivery of user notifications<br>- Integrates with the overall system to support real-time updates and user engagement, ensuring seamless communication across the application<br>- Serves as a crucial component for managing notification workflows and enhancing user experience within the platform.</td>
								</tr>
								<tr style='border-bottom: 1px solid #eee;'>
									<td style='padding: 8px;'><b><a href='https://github.com/luizmoretti/Django_ERP/blob/master/BackEnd/apps/notifications/apps.py'>apps.py</a></b></td>
									<td style='padding: 8px;'>- Defines the configuration for the notifications module within the backend architecture, establishing its identity and default settings<br>- It integrates the notifications app into the overall Django project, enabling the management and deployment of notification-related features across the system<br>- This setup ensures the notifications component is properly registered and ready for further development and integration.</td>
								</tr>
								<tr style='border-bottom: 1px solid #eee;'>
									<td style='padding: 8px;'><b><a href='https://github.com/luizmoretti/Django_ERP/blob/master/BackEnd/apps/notifications/admin.py'>admin.py</a></b></td>
									<td style='padding: 8px;'>- Facilitates administrative management of notification-related models within the Django admin interface, enabling streamlined oversight and configuration of notification data<br>- Integrates notification functionalities into the backend architecture, supporting efficient monitoring and control of notification workflows across the application<br>- This setup ensures that administrators can easily access and manage notification settings and records as part of the overall system architecture.</td>
								</tr>
								<tr style='border-bottom: 1px solid #eee;'>
									<td style='padding: 8px;'><b><a href='https://github.com/luizmoretti/Django_ERP/blob/master/BackEnd/apps/notifications/routing.py'>routing.py</a></b></td>
									<td style='padding: 8px;'>- Defines WebSocket routing for real-time notification delivery within the backend architecture<br>- It maps incoming WebSocket connection requests to the NotificationConsumer, enabling efficient, event-driven communication between the server and clients<br>- This routing setup is essential for supporting live notifications, integrating seamlessly with the overall asynchronous communication framework of the application.</td>
								</tr>
								<tr style='border-bottom: 1px solid #eee;'>
									<td style='padding: 8px;'><b><a href='https://github.com/luizmoretti/Django_ERP/blob/master/BackEnd/apps/notifications/serializers.py'>serializers.py</a></b></td>
									<td style='padding: 8px;'>- Defines serialization logic for notification data, enabling consistent transformation of notification objects into structured formats suitable for API responses<br>- Facilitates seamless data exchange between backend notification management and frontend clients, ensuring accurate and efficient delivery of notification information within the overall application architecture.</td>
								</tr>
								<tr style='border-bottom: 1px solid #eee;'>
									<td style='padding: 8px;'><b><a href='https://github.com/luizmoretti/Django_ERP/blob/master/BackEnd/apps/notifications/models.py'>models.py</a></b></td>
									<td style='padding: 8px;'>- Defines the Notification model, enabling the storage and management of user-specific notifications within the application<br>- It facilitates tracking message details, read status, and related metadata, supporting real-time alerts and user engagement features integral to the overall system architecture.</td>
								</tr>
								<tr style='border-bottom: 1px solid #eee;'>
									<td style='padding: 8px;'><b><a href='https://github.com/luizmoretti/Django_ERP/blob/master/BackEnd/apps/notifications/urls.py'>urls.py</a></b></td>
									<td style='padding: 8px;'>- Defines URL routing for notification-related endpoints within the backend architecture, facilitating communication between client requests and notification services<br>- Serves as a foundational component for integrating notification functionalities into the overall system, enabling seamless expansion and interaction with notification features across the application.</td>
								</tr>
								<tr style='border-bottom: 1px solid #eee;'>
									<td style='padding: 8px;'><b><a href='https://github.com/luizmoretti/Django_ERP/blob/master/BackEnd/apps/notifications/base.py'>base.py</a></b></td>
									<td style='padding: 8px;'>- Provides foundational functionality for managing notifications within the system by retrieving active users based on their roles and facilitating the dispatch of notifications<br>- It centralizes notification handling logic, ensuring consistent delivery across different user types and streamlining communication workflows within the applications architecture.</td>
								</tr>
								<tr style='border-bottom: 1px solid #eee;'>
									<td style='padding: 8px;'><b><a href='https://github.com/luizmoretti/Django_ERP/blob/master/BackEnd/apps/notifications/utils.py'>utils.py</a></b></td>
									<td style='padding: 8px;'>- Facilitates real-time user notifications by creating persistent records and leveraging WebSocket channels for instant delivery<br>- Supports individual and bulk notifications, integrating seamlessly with user data and application context to ensure timely, reliable communication within the overall backend architecture.</td>
								</tr>
							</table>
						</blockquote>
					</details>
					<!-- scheduller Submodule -->
					<details>
						<summary><b>scheduller</b></summary>
						<blockquote>
							<div class='directory-path' style='padding: 8px 0; color: #666;'>
								<code><b>⦿ BackEnd.apps.scheduller</b></code>
							<table style='width: 100%; border-collapse: collapse;'>
							<thead>
								<tr style='background-color: #f8f9fa;'>
									<th style='width: 30%; text-align: left; padding: 8px;'>File Name</th>
									<th style='text-align: left; padding: 8px;'>Summary</th>
								</tr>
							</thead>
								<tr style='border-bottom: 1px solid #eee;'>
									<td style='padding: 8px;'><b><a href='https://github.com/luizmoretti/Django_ERP/blob/master/BackEnd/apps/scheduller/tests.py'>tests.py</a></b></td>
									<td style='padding: 8px;'>- Provides foundational test cases for the scheduling applications backend, ensuring core functionalities operate correctly within the Django framework<br>- Serves as a safeguard for maintaining code integrity and stability, supporting the overall architecture by validating that scheduling features perform as expected during development and future updates.</td>
								</tr>
								<tr style='border-bottom: 1px solid #eee;'>
									<td style='padding: 8px;'><b><a href='https://github.com/luizmoretti/Django_ERP/blob/master/BackEnd/apps/scheduller/views.py'>views.py</a></b></td>
									<td style='padding: 8px;'>- Defines API endpoints for managing job types within the scheduling system, enabling listing, creation, retrieval, updating, and deletion of job type records<br>- Ensures operations are scoped to the users company and incorporates authentication and transaction safety, facilitating seamless integration of job scheduling functionalities into the broader application architecture.</td>
								</tr>
								<tr style='border-bottom: 1px solid #eee;'>
									<td style='padding: 8px;'><b><a href='https://github.com/luizmoretti/Django_ERP/blob/master/BackEnd/apps/scheduller/apps.py'>apps.py</a></b></td>
									<td style='padding: 8px;'>- Defines the configuration for the scheduler application within the Django project, establishing its identity and default settings<br>- It integrates the scheduler module into the overall project architecture, enabling proper registration and management of scheduler-related functionalities across the backend system<br>- This setup ensures the scheduler operates seamlessly within the Django environment.</td>
								</tr>
								<tr style='border-bottom: 1px solid #eee;'>
									<td style='padding: 8px;'><b><a href='https://github.com/luizmoretti/Django_ERP/blob/master/BackEnd/apps/scheduller/admin.py'>admin.py</a></b></td>
									<td style='padding: 8px;'>- Facilitates administrative management of scheduling-related models within the Django admin interface, enabling streamlined oversight and configuration of scheduling functionalities<br>- Integrates backend scheduling components into the overall project architecture, supporting efficient data handling and user interaction for administrative users<br>- Enhances the maintainability and usability of scheduling features across the application.</td>
								</tr>
								<tr style='border-bottom: 1px solid #eee;'>
									<td style='padding: 8px;'><b><a href='https://github.com/luizmoretti/Django_ERP/blob/master/BackEnd/apps/scheduller/serializers.py'>serializers.py</a></b></td>
									<td style='padding: 8px;'>- Defines serializers for scheduling management, enabling creation, validation, and retrieval of scheduling data and associated job types<br>- Facilitates seamless data transformation between backend models and API responses, ensuring data integrity and consistency within the scheduling architecture<br>- Supports efficient handling of schedule details, user attribution, and related job assignments across the system.</td>
								</tr>
								<tr style='border-bottom: 1px solid #eee;'>
									<td style='padding: 8px;'><b><a href='https://github.com/luizmoretti/Django_ERP/blob/master/BackEnd/apps/scheduller/models.py'>models.py</a></b></td>
									<td style='padding: 8px;'>- Defines models for managing scheduled jobs and their categories within the system<br>- Facilitates creation of custom job types and scheduling entries, enabling organized, time-bound execution of tasks across various locations<br>- Supports efficient categorization, tracking, and retrieval of scheduled activities, integrating seamlessly into the broader backend architecture for automated job management.</td>
								</tr>
								<tr style='border-bottom: 1px solid #eee;'>
									<td style='padding: 8px;'><b><a href='https://github.com/luizmoretti/Django_ERP/blob/master/BackEnd/apps/scheduller/urls.py'>urls.py</a></b></td>
									<td style='padding: 8px;'>- Defines URL endpoints for managing job type schedulers within the backend architecture, enabling clients to perform CRUD operations<br>- Integrates with view classes to facilitate listing, creating, retrieving, updating, and deleting scheduler records, thereby supporting dynamic scheduling configurations essential for orchestrating background job execution across the system.</td>
								</tr>
							</table>
							<!-- services Submodule -->
							<details>
								<summary><b>services</b></summary>
								<blockquote>
									<div class='directory-path' style='padding: 8px 0; color: #666;'>
										<code><b>⦿ BackEnd.apps.scheduller.services</b></code>
									<table style='width: 100%; border-collapse: collapse;'>
									<thead>
										<tr style='background-color: #f8f9fa;'>
											<th style='width: 30%; text-align: left; padding: 8px;'>File Name</th>
											<th style='text-align: left; padding: 8px;'>Summary</th>
										</tr>
									</thead>
										<tr style='border-bottom: 1px solid #eee;'>
											<td style='padding: 8px;'><b><a href='https://github.com/luizmoretti/Django_ERP/blob/master/BackEnd/apps/scheduller/services/handlers.py'>handlers.py</a></b></td>
											<td style='padding: 8px;'>- Facilitates the management and execution of scheduled tasks within the backend architecture, ensuring timely processing and coordination of operations<br>- Integrates with other service components to handle task lifecycle events, contributing to the overall reliability and efficiency of the applications scheduling system<br>- Supports seamless automation and operational workflows across the platform.</td>
										</tr>
										<tr style='border-bottom: 1px solid #eee;'>
											<td style='padding: 8px;'><b><a href='https://github.com/luizmoretti/Django_ERP/blob/master/BackEnd/apps/scheduller/services/validators.py'>validators.py</a></b></td>
											<td style='padding: 8px;'>- Provides validation logic for scheduling-related data inputs within the backend service, ensuring data integrity and correctness before processing<br>- Integrates with the overall architecture to enforce business rules and maintain consistent data standards across the scheduling module, supporting reliable and error-free operation of the applications scheduling functionalities.</td>
										</tr>
									</table>
								</blockquote>
							</details>
						</blockquote>
					</details>
					<!-- companies Submodule -->
					<details>
						<summary><b>companies</b></summary>
						<blockquote>
							<div class='directory-path' style='padding: 8px 0; color: #666;'>
								<code><b>⦿ BackEnd.apps.companies</b></code>
							<table style='width: 100%; border-collapse: collapse;'>
							<thead>
								<tr style='background-color: #f8f9fa;'>
									<th style='width: 30%; text-align: left; padding: 8px;'>File Name</th>
									<th style='text-align: left; padding: 8px;'>Summary</th>
								</tr>
							</thead>
								<tr style='border-bottom: 1px solid #eee;'>
									<td style='padding: 8px;'><b><a href='https://github.com/luizmoretti/Django_ERP/blob/master/BackEnd/apps/companies/tests.py'>tests.py</a></b></td>
									<td style='padding: 8px;'>- Facilitates testing of company-related functionalities within the backend application<br>- Ensures that core business logic and data interactions for companies operate correctly, supporting overall system reliability and integrity<br>- Serves as a foundational component for validating features before deployment, contributing to the robustness of the backend architecture in the context of the larger project.</td>
								</tr>
								<tr style='border-bottom: 1px solid #eee;'>
									<td style='padding: 8px;'><b><a href='https://github.com/luizmoretti/Django_ERP/blob/master/BackEnd/apps/companies/views.py'>views.py</a></b></td>
									<td style='padding: 8px;'>- Provides API endpoints for managing company data, including listing and creating companies based on user permissions<br>- Ensures secure access control, role-based visibility, and comprehensive validation, supporting organizational structure management within the broader application architecture<br>- Facilitates seamless integration of company information handling aligned with user roles and permissions.</td>
								</tr>
								<tr style='border-bottom: 1px solid #eee;'>
									<td style='padding: 8px;'><b><a href='https://github.com/luizmoretti/Django_ERP/blob/master/BackEnd/apps/companies/apps.py'>apps.py</a></b></td>
									<td style='padding: 8px;'>- Defines the configuration for the companies module within the Django project, establishing its application identity and auto-incrementing primary key setting<br>- It also ensures the registration of signal handlers upon application startup, facilitating event-driven behaviors and integrations related to company data management across the overall backend architecture.</td>
								</tr>
								<tr style='border-bottom: 1px solid #eee;'>
									<td style='padding: 8px;'><b><a href='https://github.com/luizmoretti/Django_ERP/blob/master/BackEnd/apps/companies/admin.py'>admin.py</a></b></td>
									<td style='padding: 8px;'>- Defines administrative interfaces for managing company and pickup address data within the backend system<br>- Facilitates efficient data oversight by configuring display, filtering, and search capabilities, ensuring streamlined management of company records and associated pickup locations<br>- Integrates with the overall architecture to support backend data operations and user access control for company-related entities.</td>
								</tr>
								<tr style='border-bottom: 1px solid #eee;'>
									<td style='padding: 8px;'><b><a href='https://github.com/luizmoretti/Django_ERP/blob/master/BackEnd/apps/companies/serializers.py'>serializers.py</a></b></td>
									<td style='padding: 8px;'>- Defines serializers for company and pickup address models, enabling structured data transformation and validation within the backend architecture<br>- Facilitates seamless creation, updating, and retrieval of company details and associated pickup addresses, supporting data consistency and integrity across the companys core domain functionalities<br>- Enhances API interactions by providing clear serialization logic aligned with the overall system design.</td>
								</tr>
								<tr style='border-bottom: 1px solid #eee;'>
									<td style='padding: 8px;'><b><a href='https://github.com/luizmoretti/Django_ERP/blob/master/BackEnd/apps/companies/models.py'>models.py</a></b></td>
									<td style='padding: 8px;'>- Defines the data models for managing company information and associated pickup addresses within the backend architecture<br>- Facilitates storage, retrieval, and organization of company details, including contact info, location, and operational status, supporting core functionalities related to company management and logistics workflows across the application.</td>
								</tr>
								<tr style='border-bottom: 1px solid #eee;'>
									<td style='padding: 8px;'><b><a href='https://github.com/luizmoretti/Django_ERP/blob/master/BackEnd/apps/companies/signals.py'>signals.py</a></b></td>
									<td style='padding: 8px;'>- Automates synchronization of pickup address records with company data by creating or updating PickUpCompanieAddress entries whenever a company is saved<br>- Ensures consistency between company details and associated pickup addresses, supporting seamless data integrity within the backend architecture<br>- This mechanism streamlines address management and maintains up-to-date location information across the system.</td>
								</tr>
								<tr style='border-bottom: 1px solid #eee;'>
									<td style='padding: 8px;'><b><a href='https://github.com/luizmoretti/Django_ERP/blob/master/BackEnd/apps/companies/urls.py'>urls.py</a></b></td>
									<td style='padding: 8px;'>- Defines URL routing for company-related operations within the backend architecture, enabling clients to retrieve a list of companies or create new company entries<br>- Serves as a key component in the API layer, facilitating communication between frontend requests and backend business logic for managing company data<br>- Integrates seamlessly into the overall modular structure of the application.</td>
								</tr>
							</table>
							<!-- employeers Submodule -->
							<details>
								<summary><b>employeers</b></summary>
								<blockquote>
									<div class='directory-path' style='padding: 8px 0; color: #666;'>
										<code><b>⦿ BackEnd.apps.companies.employeers</b></code>
									<table style='width: 100%; border-collapse: collapse;'>
									<thead>
										<tr style='background-color: #f8f9fa;'>
											<th style='width: 30%; text-align: left; padding: 8px;'>File Name</th>
											<th style='text-align: left; padding: 8px;'>Summary</th>
										</tr>
									</thead>
										<tr style='border-bottom: 1px solid #eee;'>
											<td style='padding: 8px;'><b><a href='https://github.com/luizmoretti/Django_ERP/blob/master/BackEnd/apps/companies/employeers/tests.py'>tests.py</a></b></td>
											<td style='padding: 8px;'>- Provides unit tests for the companies application, ensuring the correctness and reliability of employee-related functionalities within the backend architecture<br>- Supports maintaining code quality and facilitates future development by verifying that employee management features operate as intended in the overall system.</td>
										</tr>
										<tr style='border-bottom: 1px solid #eee;'>
											<td style='padding: 8px;'><b><a href='https://github.com/luizmoretti/Django_ERP/blob/master/BackEnd/apps/companies/employeers/views.py'>views.py</a></b></td>
											<td style='padding: 8px;'>- This code file defines a foundational set of API views for managing employee (employeer) data within the backend architecture<br>- It establishes standardized endpoints for creating, retrieving, updating, and deleting employee records, ensuring secure access through authentication<br>- Serving as a core component of the employees module, it facilitates consistent and efficient interactions with employee data, supporting the broader system's goal of managing organizational personnel information effectively.</td>
										</tr>
										<tr style='border-bottom: 1px solid #eee;'>
											<td style='padding: 8px;'><b><a href='https://github.com/luizmoretti/Django_ERP/blob/master/BackEnd/apps/companies/employeers/apps.py'>apps.py</a></b></td>
											<td style='padding: 8px;'>- Defines the application configuration for the employeers module within the companies domain, establishing its identity and default database auto-increment behavior<br>- It integrates the employeers functionality into the overall project architecture, enabling Django to recognize and manage the module as a distinct component for handling employee-related data and operations.</td>
										</tr>
										<tr style='border-bottom: 1px solid #eee;'>
											<td style='padding: 8px;'><b><a href='https://github.com/luizmoretti/Django_ERP/blob/master/BackEnd/apps/companies/employeers/admin.py'>admin.py</a></b></td>
											<td style='padding: 8px;'>- Defines the administrative interface for managing employer records within the backend system, enabling streamlined oversight of employer data such as hire dates, payroll schedules, and payment details<br>- Integrates with Djangos admin framework to facilitate efficient data management and ensure consistent, read-only tracking of creation and modification metadata across the application.</td>
										</tr>
										<tr style='border-bottom: 1px solid #eee;'>
											<td style='padding: 8px;'><b><a href='https://github.com/luizmoretti/Django_ERP/blob/master/BackEnd/apps/companies/employeers/serializers.py'>serializers.py</a></b></td>
											<td style='padding: 8px;'>- Defines a serializer for employee management, enabling seamless creation, retrieval, updating, and validation of employee data within the backend architecture<br>- It centralizes data handling for employee records, ensuring data integrity, unique email enforcement, and proper association with user and company entities, thereby supporting consistent and secure employee-related operations across the system.</td>
										</tr>
										<tr style='border-bottom: 1px solid #eee;'>
											<td style='padding: 8px;'><b><a href='https://github.com/luizmoretti/Django_ERP/blob/master/BackEnd/apps/companies/employeers/models.py'>models.py</a></b></td>
											<td style='padding: 8px;'>- Defines the Employee model, central to managing company staff information within the backend architecture<br>- It encapsulates personal, contact, and employment details, facilitating seamless integration with user accounts and company data<br>- This model supports automated data population and relationship management, ensuring accurate and consistent employee records across the system.</td>
										</tr>
										<tr style='border-bottom: 1px solid #eee;'>
											<td style='padding: 8px;'><b><a href='https://github.com/luizmoretti/Django_ERP/blob/master/BackEnd/apps/companies/employeers/urls.py'>urls.py</a></b></td>
											<td style='padding: 8px;'>- Defines URL routing for employer management within the backend application, facilitating core CRUD operations such as listing, creating, retrieving, updating, and deleting employer records<br>- Serves as the primary interface for client requests related to employer data, integrating with view logic to support seamless data handling and interaction within the overall project architecture.</td>
										</tr>
									</table>
								</blockquote>
							</details>
							<!-- customers Submodule -->
							<details>
								<summary><b>customers</b></summary>
								<blockquote>
									<div class='directory-path' style='padding: 8px 0; color: #666;'>
										<code><b>⦿ BackEnd.apps.companies.customers</b></code>
									<table style='width: 100%; border-collapse: collapse;'>
									<thead>
										<tr style='background-color: #f8f9fa;'>
											<th style='width: 30%; text-align: left; padding: 8px;'>File Name</th>
											<th style='text-align: left; padding: 8px;'>Summary</th>
										</tr>
									</thead>
										<tr style='border-bottom: 1px solid #eee;'>
											<td style='padding: 8px;'><b><a href='https://github.com/luizmoretti/Django_ERP/blob/master/BackEnd/apps/companies/customers/tests.py'>tests.py</a></b></td>
											<td style='padding: 8px;'>- Facilitates testing of customer-related functionalities within the backend application, ensuring the integrity and reliability of customer data handling<br>- Integrates with the overall architecture by validating components associated with customer management, contributing to the robustness of the backend services in the project<br>- Supports quality assurance processes to maintain consistent performance across the applications customer modules.</td>
										</tr>
										<tr style='border-bottom: 1px solid #eee;'>
											<td style='padding: 8px;'><b><a href='https://github.com/luizmoretti/Django_ERP/blob/master/BackEnd/apps/companies/customers/views.py'>views.py</a></b></td>
											<td style='padding: 8px;'>- The <code>views.py</code> file in the <code>BackEnd/apps/companies/customers</code> directory defines the core API endpoints for managing customer data within the application<br>- It facilitates operations such as listing, creating, retrieving, updating, and deleting customer records, ensuring these actions are performed securely and efficiently<br>- Serving as the interface between client requests and the underlying customer data models, this code enforces authentication, optimizes data retrieval, and integrates schema documentation<br>- Overall, it plays a pivotal role in enabling authorized users to interact with customer information seamlessly, supporting the broader architectures goal of robust customer management within the companys ecosystem.</td>
										</tr>
										<tr style='border-bottom: 1px solid #eee;'>
											<td style='padding: 8px;'><b><a href='https://github.com/luizmoretti/Django_ERP/blob/master/BackEnd/apps/companies/customers/apps.py'>apps.py</a></b></td>
											<td style='padding: 8px;'>- Defines the configuration for the customers module within the companies app, establishing its identity and setup within the Django project<br>- It ensures proper registration of the app and triggers the loading of relevant signals during application startup, facilitating customer-related functionalities and integrations across the backend architecture.</td>
										</tr>
										<tr style='border-bottom: 1px solid #eee;'>
											<td style='padding: 8px;'><b><a href='https://github.com/luizmoretti/Django_ERP/blob/master/BackEnd/apps/companies/customers/admin.py'>admin.py</a></b></td>
											<td style='padding: 8px;'>- Defines administrative interfaces for managing customer data, including personal details, project addresses, and billing addresses within the backend<br>- Facilitates efficient oversight and editing of customer-related information, supporting overall data integrity and accessibility across the applications architecture<br>- Enhances the backends capability to handle customer records systematically and securely.</td>
										</tr>
										<tr style='border-bottom: 1px solid #eee;'>
											<td style='padding: 8px;'><b><a href='https://github.com/luizmoretti/Django_ERP/blob/master/BackEnd/apps/companies/customers/serializers.py'>serializers.py</a></b></td>
											<td style='padding: 8px;'>- Defines serializers for managing customer and lead data within the backend architecture<br>- Facilitates creation, update, and retrieval of customer profiles, including addresses and associated company details, as well as handling business lead information from external sources<br>- Ensures data validation and structured representation aligned with the overall systems data flow and integrity.</td>
										</tr>
										<tr style='border-bottom: 1px solid #eee;'>
											<td style='padding: 8px;'><b><a href='https://github.com/luizmoretti/Django_ERP/blob/master/BackEnd/apps/companies/customers/models.py'>models.py</a></b></td>
											<td style='padding: 8px;'>- Defines comprehensive models for managing customer data, addresses, and leads within the system architecture<br>- Facilitates tracking of customer contact details, billing and shipping addresses, and potential business leads sourced from external platforms like Google Local Search<br>- Supports data integrity and relationship management across companies, employees, and external lead sources, enabling efficient customer relationship and sales pipeline management.</td>
										</tr>
										<tr style='border-bottom: 1px solid #eee;'>
											<td style='padding: 8px;'><b><a href='https://github.com/luizmoretti/Django_ERP/blob/master/BackEnd/apps/companies/customers/signals.py'>signals.py</a></b></td>
											<td style='padding: 8px;'>- Automates the creation of associated customer addresses upon new customer registration, ensuring data consistency within the applications architecture<br>- It streamlines the onboarding process by generating project and billing addresses based on customer flags, facilitating seamless integration of customer-related data and maintaining integrity across related models.</td>
										</tr>
										<tr style='border-bottom: 1px solid #eee;'>
											<td style='padding: 8px;'><b><a href='https://github.com/luizmoretti/Django_ERP/blob/master/BackEnd/apps/companies/customers/services.py'>services.py</a></b></td>
											<td style='padding: 8px;'>- This code file defines the <code>CustomerService</code> class, which provides core functionalities for managing customer data within the backend architecture<br>- Its primary purpose is to facilitate flexible retrieval of customer information based on various filtering criteria, such as customer ID, name, or associated company ID<br>- This service acts as an abstraction layer that centralizes customer-related operations, ensuring consistent data access patterns across the application<br>- It plays a crucial role in supporting features that require customer data, integrating seamlessly with other modules like addresses and leads, and contributing to the overall modular and scalable architecture of the system.</td>
										</tr>
										<tr style='border-bottom: 1px solid #eee;'>
											<td style='padding: 8px;'><b><a href='https://github.com/luizmoretti/Django_ERP/blob/master/BackEnd/apps/companies/customers/urls.py'>urls.py</a></b></td>
											<td style='padding: 8px;'>- Defines URL routing for customer-related operations within the backend, enabling functionalities such as listing, creating, retrieving by ID or name, updating, and deleting customer records<br>- Additionally, facilitates lead generation and listing for customers, integrating core customer management features into the overall application architecture.</td>
										</tr>
									</table>
									<!-- utils Submodule -->
									<details>
										<summary><b>utils</b></summary>
										<blockquote>
											<div class='directory-path' style='padding: 8px 0; color: #666;'>
												<code><b>⦿ BackEnd.apps.companies.customers.utils</b></code>
											<table style='width: 100%; border-collapse: collapse;'>
											<thead>
												<tr style='background-color: #f8f9fa;'>
													<th style='width: 30%; text-align: left; padding: 8px;'>File Name</th>
													<th style='text-align: left; padding: 8px;'>Summary</th>
												</tr>
											</thead>
												<tr style='border-bottom: 1px solid #eee;'>
													<td style='padding: 8px;'><b><a href='https://github.com/luizmoretti/Django_ERP/blob/master/BackEnd/apps/companies/customers/utils/google_scraper_serpapi.py'>google_scraper_serpapi.py</a></b></td>
													<td style='padding: 8px;'>- Facilitates asynchronous and synchronous retrieval of local business data from Google via SerpAPI, integrating with Django caching for efficiency<br>- Supports multi-page fetching, processes raw API responses into structured business profiles, and enables user-driven searches with optional result limits<br>- Enhances customer data enrichment by providing accurate, up-to-date local business information within the broader backend architecture.</td>
												</tr>
											</table>
										</blockquote>
									</details>
								</blockquote>
							</details>
							<!-- attendance Submodule -->
							<details>
								<summary><b>attendance</b></summary>
								<blockquote>
									<div class='directory-path' style='padding: 8px 0; color: #666;'>
										<code><b>⦿ BackEnd.apps.companies.attendance</b></code>
									<table style='width: 100%; border-collapse: collapse;'>
									<thead>
										<tr style='background-color: #f8f9fa;'>
											<th style='width: 30%; text-align: left; padding: 8px;'>File Name</th>
											<th style='text-align: left; padding: 8px;'>Summary</th>
										</tr>
									</thead>
										<tr style='border-bottom: 1px solid #eee;'>
											<td style='padding: 8px;'><b><a href='https://github.com/luizmoretti/Django_ERP/blob/master/BackEnd/apps/companies/attendance/tests.py'>tests.py</a></b></td>
											<td style='padding: 8px;'>- Facilitates validation of attendance-related functionalities within the companies application by providing test cases<br>- Ensures the integrity and correctness of attendance features, supporting reliable performance within the broader backend architecture<br>- Serves as a foundation for maintaining quality and stability in attendance management workflows across the project.</td>
										</tr>
										<tr style='border-bottom: 1px solid #eee;'>
											<td style='padding: 8px;'><b><a href='https://github.com/luizmoretti/Django_ERP/blob/master/BackEnd/apps/companies/attendance/views.py'>views.py</a></b></td>
											<td style='padding: 8px;'>- Defines API endpoints for managing employee attendance and payroll within the companys architecture<br>- Facilitates listing, creating, retrieving, updating, and deleting attendance records, as well as clock-in/out operations and payroll processing<br>- Ensures secure, validated interactions aligned with user permissions, supporting seamless attendance tracking and payroll workflows across the organizational structure.</td>
										</tr>
										<tr style='border-bottom: 1px solid #eee;'>
											<td style='padding: 8px;'><b><a href='https://github.com/luizmoretti/Django_ERP/blob/master/BackEnd/apps/companies/attendance/apps.py'>apps.py</a></b></td>
											<td style='padding: 8px;'>- Defines the application configuration for the attendance module within the companies ecosystem, establishing its integration point in the Django project<br>- It ensures proper setup and initialization, including the registration of signal handlers that facilitate event-driven responses related to attendance management across the platform<br>- This configuration is essential for maintaining modularity and cohesive operation within the overall architecture.</td>
										</tr>
										<tr style='border-bottom: 1px solid #eee;'>
											<td style='padding: 8px;'><b><a href='https://github.com/luizmoretti/Django_ERP/blob/master/BackEnd/apps/companies/attendance/admin.py'>admin.py</a></b></td>
											<td style='padding: 8px;'>- Defines administrative interfaces for managing employee attendance, time tracking, payroll, and payroll history within the backend system<br>- Facilitates streamlined data entry, visualization, and access control, ensuring accurate tracking of employee work hours, attendance records, and payroll processing aligned with different payment types<br>- Integrates seamlessly into the overall architecture to support HR and payroll operations efficiently.</td>
										</tr>
										<tr style='border-bottom: 1px solid #eee;'>
											<td style='padding: 8px;'><b><a href='https://github.com/luizmoretti/Django_ERP/blob/master/BackEnd/apps/companies/attendance/serializers.py'>serializers.py</a></b></td>
											<td style='padding: 8px;'>- Defines serializers for managing employee attendance, work tracking, and payroll processes within the backend architecture<br>- Facilitates data validation, creation, and updates of attendance records, clock-in/out operations, and payroll payments, ensuring seamless integration between employee work data and payroll systems<br>- Supports robust data handling and consistency across attendance and compensation workflows.</td>
										</tr>
										<tr style='border-bottom: 1px solid #eee;'>
											<td style='padding: 8px;'><b><a href='https://github.com/luizmoretti/Django_ERP/blob/master/BackEnd/apps/companies/attendance/models.py'>models.py</a></b></td>
											<td style='padding: 8px;'>- Defines data models for managing employee attendance, time tracking, and payroll processes within the application<br>- Facilitates recording clock-in/out times, daily attendance, and payroll calculations, ensuring accurate tracking of work hours and payment statuses<br>- Supports comprehensive attendance and payroll management aligned with employee payment types, enabling efficient workforce administration and financial reconciliation.</td>
										</tr>
										<tr style='border-bottom: 1px solid #eee;'>
											<td style='padding: 8px;'><b><a href='https://github.com/luizmoretti/Django_ERP/blob/master/BackEnd/apps/companies/attendance/signals.py'>signals.py</a></b></td>
											<td style='padding: 8px;'>- Automates payroll management by synchronizing employee time tracking with payroll records, ensuring accurate calculation of hours, days, and amounts for both hourly and daily workers<br>- Maintains payroll history upon payment completion, supporting seamless updates and data integrity within the overall attendance and compensation architecture.</td>
										</tr>
										<tr style='border-bottom: 1px solid #eee;'>
											<td style='padding: 8px;'><b><a href='https://github.com/luizmoretti/Django_ERP/blob/master/BackEnd/apps/companies/attendance/urls.py'>urls.py</a></b></td>
											<td style='padding: 8px;'>- Defines URL routing for the attendance management module, enabling CRUD operations, clock-in/out functionality, and payroll processing<br>- Integrates various views to facilitate employee attendance tracking, time registration, and payroll payments within the backend architecture, supporting seamless interaction between frontend requests and backend data handling.</td>
										</tr>
									</table>
									<!-- services Submodule -->
									<details>
										<summary><b>services</b></summary>
										<blockquote>
											<div class='directory-path' style='padding: 8px 0; color: #666;'>
												<code><b>⦿ BackEnd.apps.companies.attendance.services</b></code>
											<table style='width: 100%; border-collapse: collapse;'>
											<thead>
												<tr style='background-color: #f8f9fa;'>
													<th style='width: 30%; text-align: left; padding: 8px;'>File Name</th>
													<th style='text-align: left; padding: 8px;'>Summary</th>
												</tr>
											</thead>
												<tr style='border-bottom: 1px solid #eee;'>
													<td style='padding: 8px;'><b><a href='https://github.com/luizmoretti/Django_ERP/blob/master/BackEnd/apps/companies/attendance/services/reports.py'>reports.py</a></b></td>
													<td style='padding: 8px;'>- Provides comprehensive services for generating attendance and payroll reports within the companys architecture<br>- Facilitates summary, detailed, and filtered reports for overall company, individual employees, and specific periods, integrating attendance, time tracking, days tracking, and payroll data to support operational and financial insights.</td>
												</tr>
												<tr style='border-bottom: 1px solid #eee;'>
													<td style='padding: 8px;'><b><a href='https://github.com/luizmoretti/Django_ERP/blob/master/BackEnd/apps/companies/attendance/services/handlers.py'>handlers.py</a></b></td>
													<td style='padding: 8px;'>- The <code>handlers.py</code> file within the attendance services module serves as the core business logic layer for managing employee attendance and payroll-related data<br>- It orchestrates the creation, validation, and processing of attendance records, ensuring accurate tracking of work hours and days<br>- This component enforces business rules, maintains data integrity through transactional operations, and integrates with employee and payroll models to support comprehensive attendance management within the larger system architecture.</td>
												</tr>
												<tr style='border-bottom: 1px solid #eee;'>
													<td style='padding: 8px;'><b><a href='https://github.com/luizmoretti/Django_ERP/blob/master/BackEnd/apps/companies/attendance/services/validators.py'>validators.py</a></b></td>
													<td style='padding: 8px;'>- Provides comprehensive validation for attendance, payroll, and report operations within the backend architecture<br>- Ensures data integrity, enforces business rules, and maintains security by verifying user access, data formats, status transitions, and report parameters, thereby supporting reliable and compliant attendance and payroll management processes across the companys systems.</td>
												</tr>
											</table>
										</blockquote>
									</details>
								</blockquote>
							</details>
						</blockquote>
					</details>
					<!-- accounts Submodule -->
					<details>
						<summary><b>accounts</b></summary>
						<blockquote>
							<div class='directory-path' style='padding: 8px 0; color: #666;'>
								<code><b>⦿ BackEnd.apps.accounts</b></code>
							<table style='width: 100%; border-collapse: collapse;'>
							<thead>
								<tr style='background-color: #f8f9fa;'>
									<th style='width: 30%; text-align: left; padding: 8px;'>File Name</th>
									<th style='text-align: left; padding: 8px;'>Summary</th>
								</tr>
							</thead>
								<tr style='border-bottom: 1px solid #eee;'>
									<td style='padding: 8px;'><b><a href='https://github.com/luizmoretti/Django_ERP/blob/master/BackEnd/apps/accounts/tests.py'>tests.py</a></b></td>
									<td style='padding: 8px;'>- Facilitates validation of account-related functionalities within the backend application<br>- Ensures that user account operations perform correctly and reliably, contributing to the overall integrity of the user management system<br>- Supports maintaining high-quality standards by providing a foundation for automated testing of account features in the Django-based architecture.</td>
								</tr>
								<tr style='border-bottom: 1px solid #eee;'>
									<td style='padding: 8px;'><b><a href='https://github.com/luizmoretti/Django_ERP/blob/master/BackEnd/apps/accounts/views.py'>views.py</a></b></td>
									<td style='padding: 8px;'>- This code file defines the core API endpoints for user account management within the backend architecture<br>- It facilitates essential user operations such as registration, authentication, login, and password reset, serving as the primary interface for user-related interactions<br>- By integrating with Django REST Framework and supporting token-based authentication, it ensures secure and scalable user access control across the application<br>- Overall, this module is pivotal in managing user identities and access within the systems broader service-oriented architecture.</td>
								</tr>
								<tr style='border-bottom: 1px solid #eee;'>
									<td style='padding: 8px;'><b><a href='https://github.com/luizmoretti/Django_ERP/blob/master/BackEnd/apps/accounts/apps.py'>apps.py</a></b></td>
									<td style='padding: 8px;'>- Defines the configuration for the accounts module, orchestrating setup and signal registration to facilitate user management, permission handling, and IP tracking<br>- Ensures that all custom signals related to employee creation, group assignment, and login activities are properly connected during application startup, supporting core account functionalities within the overall system architecture.</td>
								</tr>
								<tr style='border-bottom: 1px solid #eee;'>
									<td style='padding: 8px;'><b><a href='https://github.com/luizmoretti/Django_ERP/blob/master/BackEnd/apps/accounts/admin.py'>admin.py</a></b></td>
									<td style='padding: 8px;'>- Defines the administrative interface for managing custom user accounts within the backend system<br>- It facilitates user creation, modification, and filtering, ensuring streamlined user management aligned with project-specific user types and permissions<br>- This setup integrates seamlessly into the overall architecture, supporting secure and efficient handling of user data through Djangos admin framework.</td>
								</tr>
								<tr style='border-bottom: 1px solid #eee;'>
									<td style='padding: 8px;'><b><a href='https://github.com/luizmoretti/Django_ERP/blob/master/BackEnd/apps/accounts/serializers.py'>serializers.py</a></b></td>
									<td style='padding: 8px;'>- Defines serializers for user management, authentication, and password validation within the backend architecture<br>- Facilitates secure user creation, updates, and login processes while enforcing data integrity and security standards<br>- Supports role-based access control and permission handling, serving as the core interface for user-related data operations across the system.</td>
								</tr>
								<tr style='border-bottom: 1px solid #eee;'>
									<td style='padding: 8px;'><b><a href='https://github.com/luizmoretti/Django_ERP/blob/master/BackEnd/apps/accounts/models.py'>models.py</a></b></td>
									<td style='padding: 8px;'>- Defines a custom user model leveraging email as the primary identifier, supporting diverse user types such as employees, customers, and suppliers<br>- Incorporates UUIDs for unique identification and tracks user IP addresses upon login<br>- Facilitates flexible user management within the broader application architecture, ensuring secure authentication and user data consistency across the system.</td>
								</tr>
								<tr style='border-bottom: 1px solid #eee;'>
									<td style='padding: 8px;'><b><a href='https://github.com/luizmoretti/Django_ERP/blob/master/BackEnd/apps/accounts/signals.py'>signals.py</a></b></td>
									<td style='padding: 8px;'>- Manages user lifecycle events, including automatic creation of company and employee records, group assignment based on user type, and permission synchronization<br>- Ensures consistent user permissions and group memberships across the system, handles updates on user type changes, and tracks login IP addresses, thereby maintaining data integrity and access control within the overall application architecture.</td>
								</tr>
								<tr style='border-bottom: 1px solid #eee;'>
									<td style='padding: 8px;'><b><a href='https://github.com/luizmoretti/Django_ERP/blob/master/BackEnd/apps/accounts/urls.py'>urls.py</a></b></td>
									<td style='padding: 8px;'>- Defines URL routing for user authentication, management, and password reset workflows within the backend application<br>- Facilitates access to login, logout, user CRUD operations, and password recovery endpoints, integrating web interface and API functionalities to support secure user account handling across the system.</td>
								</tr>
							</table>
							<!-- profiles Submodule -->
							<details>
								<summary><b>profiles</b></summary>
								<blockquote>
									<div class='directory-path' style='padding: 8px 0; color: #666;'>
										<code><b>⦿ BackEnd.apps.accounts.profiles</b></code>
									<table style='width: 100%; border-collapse: collapse;'>
									<thead>
										<tr style='background-color: #f8f9fa;'>
											<th style='width: 30%; text-align: left; padding: 8px;'>File Name</th>
											<th style='text-align: left; padding: 8px;'>Summary</th>
										</tr>
									</thead>
										<tr style='border-bottom: 1px solid #eee;'>
											<td style='padding: 8px;'><b><a href='https://github.com/luizmoretti/Django_ERP/blob/master/BackEnd/apps/accounts/profiles/views.py'>views.py</a></b></td>
											<td style='padding: 8px;'>- Defines RESTful API endpoints for managing user profiles within the application, enabling listing, retrieval, creation, updating, deletion, and avatar management<br>- Ensures proper permission checks, transactional integrity, and detailed logging, facilitating seamless profile operations aligned with company-specific data access controls in the overall backend architecture.</td>
										</tr>
										<tr style='border-bottom: 1px solid #eee;'>
											<td style='padding: 8px;'><b><a href='https://github.com/luizmoretti/Django_ERP/blob/master/BackEnd/apps/accounts/profiles/apps.py'>apps.py</a></b></td>
											<td style='padding: 8px;'>- Defines the configuration for the user profiles module within the backend architecture, establishing its identity and integrating signal handlers upon application startup<br>- This setup ensures that user profile-related functionalities and event-driven behaviors are properly initialized, supporting modularity and maintainability within the overall system.</td>
										</tr>
										<tr style='border-bottom: 1px solid #eee;'>
											<td style='padding: 8px;'><b><a href='https://github.com/luizmoretti/Django_ERP/blob/master/BackEnd/apps/accounts/profiles/admin.py'>admin.py</a></b></td>
											<td style='padding: 8px;'>- Defines the administrative interface for managing user profiles within the backend system, enabling efficient oversight of profile data<br>- It facilitates search, filtering, and display customization for user profiles, supporting streamlined data management and ensuring consistency across the applications user account architecture<br>- This component integrates seamlessly into the overall backend architecture to support user-related operations.</td>
										</tr>
										<tr style='border-bottom: 1px solid #eee;'>
											<td style='padding: 8px;'><b><a href='https://github.com/luizmoretti/Django_ERP/blob/master/BackEnd/apps/accounts/profiles/serializers.py'>serializers.py</a></b></td>
											<td style='padding: 8px;'>- Defines serializers for user profile management, enabling creation, retrieval, updating, and avatar handling within the backend architecture<br>- Facilitates data validation, serialization, and secure updates of comprehensive profile information, supporting seamless integration with user and company data models to ensure consistent and secure profile operations across the system.</td>
										</tr>
										<tr style='border-bottom: 1px solid #eee;'>
											<td style='padding: 8px;'><b><a href='https://github.com/luizmoretti/Django_ERP/blob/master/BackEnd/apps/accounts/profiles/models.py'>models.py</a></b></td>
											<td style='padding: 8px;'>- Defines the user profile model, centralizing extended user information within the application architecture<br>- It integrates personal details, professional roles, social links, and preferences, serving as a key component for managing user-specific data and enhancing personalization across the platform<br>- This model supports user identity, activity, and access control within the broader system.</td>
										</tr>
										<tr style='border-bottom: 1px solid #eee;'>
											<td style='padding: 8px;'><b><a href='https://github.com/luizmoretti/Django_ERP/blob/master/BackEnd/apps/accounts/profiles/signals.py'>signals.py</a></b></td>
											<td style='padding: 8px;'>- Automates user profile creation upon new user registration, ensuring data consistency and seamless integration with the audit system<br>- Maintains synchronization of core user information and assigns default preferences, supporting the overall architectures focus on user data integrity and operational efficiency within the backend account management system.</td>
										</tr>
										<tr style='border-bottom: 1px solid #eee;'>
											<td style='padding: 8px;'><b><a href='https://github.com/luizmoretti/Django_ERP/blob/master/BackEnd/apps/accounts/profiles/urls.py'>urls.py</a></b></td>
											<td style='padding: 8px;'>- Defines URL routing for user profile management within the backend architecture, enabling operations such as listing, viewing, creating, updating, deleting, and updating avatars<br>- Facilitates seamless interaction with profile-related endpoints, integrating profile functionalities into the overall application flow and ensuring organized access to user profile data.</td>
										</tr>
									</table>
									<!-- notifications Submodule -->
									<details>
										<summary><b>notifications</b></summary>
										<blockquote>
											<div class='directory-path' style='padding: 8px 0; color: #666;'>
												<code><b>⦿ BackEnd.apps.accounts.profiles.notifications</b></code>
											<table style='width: 100%; border-collapse: collapse;'>
											<thead>
												<tr style='background-color: #f8f9fa;'>
													<th style='width: 30%; text-align: left; padding: 8px;'>File Name</th>
													<th style='text-align: left; padding: 8px;'>Summary</th>
												</tr>
											</thead>
												<tr style='border-bottom: 1px solid #eee;'>
													<td style='padding: 8px;'><b><a href='https://github.com/luizmoretti/Django_ERP/blob/master/BackEnd/apps/accounts/profiles/notifications/constants.py'>constants.py</a></b></td>
													<td style='padding: 8px;'>- Defines constants for profile notification management, including notification types, titles, messages, severity levels, priorities, and recipient groups<br>- Facilitates consistent and centralized handling of profile-related notifications across the application, ensuring clear communication and appropriate alerting for profile events within the overall system architecture.</td>
												</tr>
												<tr style='border-bottom: 1px solid #eee;'>
													<td style='padding: 8px;'><b><a href='https://github.com/luizmoretti/Django_ERP/blob/master/BackEnd/apps/accounts/profiles/notifications/handlers.py'>handlers.py</a></b></td>
													<td style='padding: 8px;'>- Facilitates profile-related notifications by handling creation, update, deletion, and avatar change events<br>- Integrates with Django signals to automatically trigger notifications, ensuring relevant users are informed of profile lifecycle changes and updates within the application<br>- Supports maintaining user engagement and awareness through consistent, automated messaging aligned with profile activities.</td>
												</tr>
											</table>
										</blockquote>
									</details>
									<!-- services Submodule -->
									<details>
										<summary><b>services</b></summary>
										<blockquote>
											<div class='directory-path' style='padding: 8px 0; color: #666;'>
												<code><b>⦿ BackEnd.apps.accounts.profiles.services</b></code>
											<table style='width: 100%; border-collapse: collapse;'>
											<thead>
												<tr style='background-color: #f8f9fa;'>
													<th style='width: 30%; text-align: left; padding: 8px;'>File Name</th>
													<th style='text-align: left; padding: 8px;'>Summary</th>
												</tr>
											</thead>
												<tr style='border-bottom: 1px solid #eee;'>
													<td style='padding: 8px;'><b><a href='https://github.com/luizmoretti/Django_ERP/blob/master/BackEnd/apps/accounts/profiles/services/filters.py'>filters.py</a></b></td>
													<td style='padding: 8px;'>- Defines filtering and pagination mechanisms for Profile views, enabling efficient querying based on search terms, creation dates, and activity status<br>- Facilitates flexible data retrieval within the backend architecture, supporting user-centric profile management and optimized data presentation through customizable pagination<br>- Enhances the overall systems responsiveness and user experience by streamlining profile data access.</td>
												</tr>
												<tr style='border-bottom: 1px solid #eee;'>
													<td style='padding: 8px;'><b><a href='https://github.com/luizmoretti/Django_ERP/blob/master/BackEnd/apps/accounts/profiles/services/handlers.py'>handlers.py</a></b></td>
													<td style='padding: 8px;'>- Provides core profile management functionalities, including retrieval, updates, avatar handling, soft deletion, and filtering of user profiles<br>- Ensures permission checks and data validation to maintain data integrity and security within the broader backend architecture, facilitating seamless user profile operations across the application.</td>
												</tr>
												<tr style='border-bottom: 1px solid #eee;'>
													<td style='padding: 8px;'><b><a href='https://github.com/luizmoretti/Django_ERP/blob/master/BackEnd/apps/accounts/profiles/services/validators.py'>validators.py</a></b></td>
													<td style='padding: 8px;'>- Validate user profile data to ensure accuracy and consistency across the application<br>- It enforces rules and constraints during profile creation and updates, maintaining data integrity within the broader account management system<br>- This component plays a crucial role in safeguarding the quality of user information, supporting reliable user interactions and seamless integration with other backend services.</td>
												</tr>
											</table>
										</blockquote>
									</details>
								</blockquote>
							</details>
							<!-- management Submodule -->
							<details>
								<summary><b>management</b></summary>
								<blockquote>
									<div class='directory-path' style='padding: 8px 0; color: #666;'>
										<code><b>⦿ BackEnd.apps.accounts.management</b></code>
									<!-- commands Submodule -->
									<details>
										<summary><b>commands</b></summary>
										<blockquote>
											<div class='directory-path' style='padding: 8px 0; color: #666;'>
												<code><b>⦿ BackEnd.apps.accounts.management.commands</b></code>
											<table style='width: 100%; border-collapse: collapse;'>
											<thead>
												<tr style='background-color: #f8f9fa;'>
													<th style='width: 30%; text-align: left; padding: 8px;'>File Name</th>
													<th style='text-align: left; padding: 8px;'>Summary</th>
												</tr>
											</thead>
												<tr style='border-bottom: 1px solid #eee;'>
													<td style='padding: 8px;'><b><a href='https://github.com/luizmoretti/Django_ERP/blob/master/BackEnd/apps/accounts/management/commands/setup_permission_groups.py'>setup_permission_groups.py</a></b></td>
													<td style='padding: 8px;'>- Defines a Django management command to automate the creation and configuration of user groups with role-specific permissions across the application<br>- It ensures proper access control by assigning granular permissions based on user roles and app mappings, and synchronizes user permissions accordingly, supporting a structured and scalable permission management system within the overall architecture.</td>
												</tr>
											</table>
										</blockquote>
									</details>
								</blockquote>
							</details>
						</blockquote>
					</details>
					<!-- vehicle Submodule -->
					<details>
						<summary><b>vehicle</b></summary>
						<blockquote>
							<div class='directory-path' style='padding: 8px 0; color: #666;'>
								<code><b>⦿ BackEnd.apps.vehicle</b></code>
							<table style='width: 100%; border-collapse: collapse;'>
							<thead>
								<tr style='background-color: #f8f9fa;'>
									<th style='width: 30%; text-align: left; padding: 8px;'>File Name</th>
									<th style='text-align: left; padding: 8px;'>Summary</th>
								</tr>
							</thead>
								<tr style='border-bottom: 1px solid #eee;'>
									<td style='padding: 8px;'><b><a href='https://github.com/luizmoretti/Django_ERP/blob/master/BackEnd/apps/vehicle/tests.py'>tests.py</a></b></td>
									<td style='padding: 8px;'>- Provides a foundation for testing vehicle-related functionalities within the backend application, ensuring the correctness and reliability of vehicle data handling and operations<br>- Integrates with the Django testing framework to validate features and maintain code quality across the vehicle management module, supporting overall system stability and robustness in the project architecture.</td>
								</tr>
								<tr style='border-bottom: 1px solid #eee;'>
									<td style='padding: 8px;'><b><a href='https://github.com/luizmoretti/Django_ERP/blob/master/BackEnd/apps/vehicle/views.py'>views.py</a></b></td>
									<td style='padding: 8px;'>- Defines RESTful API endpoints for managing vehicle data within a multi-tenant architecture, enabling listing, creation, retrieval, updating, deletion, and driver assignment<br>- Ensures operations are scoped to the users company, incorporates validation, transaction safety, and detailed documentation, facilitating comprehensive vehicle lifecycle management and driver associations in the backend system.</td>
								</tr>
								<tr style='border-bottom: 1px solid #eee;'>
									<td style='padding: 8px;'><b><a href='https://github.com/luizmoretti/Django_ERP/blob/master/BackEnd/apps/vehicle/apps.py'>apps.py</a></b></td>
									<td style='padding: 8px;'>- Defines the configuration for the vehicle management module within the Django project, establishing its identity and default settings<br>- It integrates the vehicle app into the overall architecture, enabling seamless registration and interaction with other components<br>- This setup facilitates organized development and deployment of vehicle-related features across the backend system.</td>
								</tr>
								<tr style='border-bottom: 1px solid #eee;'>
									<td style='padding: 8px;'><b><a href='https://github.com/luizmoretti/Django_ERP/blob/master/BackEnd/apps/vehicle/admin.py'>admin.py</a></b></td>
									<td style='padding: 8px;'>- Facilitates administrative management of vehicle-related data within the backend system<br>- Integrates vehicle models into the Django admin interface, enabling streamlined data entry, updates, and oversight<br>- Supports overall architecture by providing a centralized, user-friendly platform for backend administrators to efficiently oversee vehicle information, ensuring data consistency and ease of maintenance across the applications vehicle module.</td>
								</tr>
								<tr style='border-bottom: 1px solid #eee;'>
									<td style='padding: 8px;'><b><a href='https://github.com/luizmoretti/Django_ERP/blob/master/BackEnd/apps/vehicle/serializers.py'>serializers.py</a></b></td>
									<td style='padding: 8px;'>- Defines serialization logic for Vehicle entities, enabling seamless conversion between Vehicle model instances and API-compatible data formats<br>- Facilitates validation, creation, and updating of vehicle records while ensuring data integrity and consistency across the system<br>- Supports integration with related models such as drivers and companies, serving as a core component for vehicle management within the applications architecture.</td>
								</tr>
								<tr style='border-bottom: 1px solid #eee;'>
									<td style='padding: 8px;'><b><a href='https://github.com/luizmoretti/Django_ERP/blob/master/BackEnd/apps/vehicle/models.py'>models.py</a></b></td>
									<td style='padding: 8px;'>- Defines the vehicle data model within the backend architecture, encapsulating vehicle identification, specifications, and assignment details crucial for managing fleet assets<br>- Supports tracking vehicle status, attributes, and driver associations, enabling efficient fleet management and operational workflows across delivery and logistics processes.</td>
								</tr>
								<tr style='border-bottom: 1px solid #eee;'>
									<td style='padding: 8px;'><b><a href='https://github.com/luizmoretti/Django_ERP/blob/master/BackEnd/apps/vehicle/urls.py'>urls.py</a></b></td>
									<td style='padding: 8px;'>- Defines URL routing for vehicle management, enabling CRUD operations within the backend architecture<br>- Facilitates interaction with vehicle data by mapping HTTP endpoints to corresponding views, supporting seamless creation, retrieval, updating, and deletion of vehicle records in the system<br>- Integrates with the overall API structure to ensure organized and accessible vehicle-related functionalities.</td>
								</tr>
							</table>
							<!-- services Submodule -->
							<details>
								<summary><b>services</b></summary>
								<blockquote>
									<div class='directory-path' style='padding: 8px 0; color: #666;'>
										<code><b>⦿ BackEnd.apps.vehicle.services</b></code>
									<table style='width: 100%; border-collapse: collapse;'>
									<thead>
										<tr style='background-color: #f8f9fa;'>
											<th style='width: 30%; text-align: left; padding: 8px;'>File Name</th>
											<th style='text-align: left; padding: 8px;'>Summary</th>
										</tr>
									</thead>
										<tr style='border-bottom: 1px solid #eee;'>
											<td style='padding: 8px;'><b><a href='https://github.com/luizmoretti/Django_ERP/blob/master/BackEnd/apps/vehicle/services/handlers.py'>handlers.py</a></b></td>
											<td style='padding: 8px;'>- Provides core business logic for managing vehicle lifecycle operations, including creation, updates, deletion, driver assignment, and status changes<br>- Ensures adherence to validation rules, enforces permissions, and maintains data integrity within the vehicle management architecture, supporting seamless integration with other system components and maintaining consistent operational workflows.</td>
										</tr>
										<tr style='border-bottom: 1px solid #eee;'>
											<td style='padding: 8px;'><b><a href='https://github.com/luizmoretti/Django_ERP/blob/master/BackEnd/apps/vehicle/services/validators.py'>validators.py</a></b></td>
											<td style='padding: 8px;'>- Provides validation logic for vehicle-related operations, ensuring compliance with business rules such as company access control, uniqueness of identifiers, and dependency checks before deletion<br>- Facilitates data integrity and security within the vehicle management system, supporting consistent enforcement of operational constraints across the applications architecture.</td>
										</tr>
									</table>
								</blockquote>
							</details>
						</blockquote>
					</details>
					<!-- inventory Submodule -->
					<details>
						<summary><b>inventory</b></summary>
						<blockquote>
							<div class='directory-path' style='padding: 8px 0; color: #666;'>
								<code><b>⦿ BackEnd.apps.inventory</b></code>
							<table style='width: 100%; border-collapse: collapse;'>
							<thead>
								<tr style='background-color: #f8f9fa;'>
									<th style='width: 30%; text-align: left; padding: 8px;'>File Name</th>
									<th style='text-align: left; padding: 8px;'>Summary</th>
								</tr>
							</thead>
								<tr style='border-bottom: 1px solid #eee;'>
									<td style='padding: 8px;'><b><a href='https://github.com/luizmoretti/Django_ERP/blob/master/BackEnd/apps/inventory/apps.py'>apps.py</a></b></td>
									<td style='padding: 8px;'>- Defines the configuration for the inventory module within the Django project, establishing its identity and default settings<br>- It integrates the inventory app into the overall application architecture, enabling Django to recognize and manage inventory-related functionalities as a cohesive component of the backend system.</td>
								</tr>
								<tr style='border-bottom: 1px solid #eee;'>
									<td style='padding: 8px;'><b><a href='https://github.com/luizmoretti/Django_ERP/blob/master/BackEnd/apps/inventory/README.md'>README.md</a></b></td>
									<td style='padding: 8px;'>- Provides comprehensive management of inventory movements, including inflows, outflows, and transfers, ensuring accurate stock tracking across warehouses, suppliers, and customers<br>- Facilitates validation, status updates, and real-time notifications, maintaining data integrity and operational efficiency within the broader inventory system architecture<br>- Supports seamless coordination between stock operations and user notifications for effective inventory oversight.</td>
								</tr>
							</table>
							<!-- product Submodule -->
							<details>
								<summary><b>product</b></summary>
								<blockquote>
									<div class='directory-path' style='padding: 8px 0; color: #666;'>
										<code><b>⦿ BackEnd.apps.inventory.product</b></code>
									<table style='width: 100%; border-collapse: collapse;'>
									<thead>
										<tr style='background-color: #f8f9fa;'>
											<th style='width: 30%; text-align: left; padding: 8px;'>File Name</th>
											<th style='text-align: left; padding: 8px;'>Summary</th>
										</tr>
									</thead>
										<tr style='border-bottom: 1px solid #eee;'>
											<td style='padding: 8px;'><b><a href='https://github.com/luizmoretti/Django_ERP/blob/master/BackEnd/apps/inventory/product/tests.py'>tests.py</a></b></td>
											<td style='padding: 8px;'>- Provides unit tests for the inventory product module, ensuring the correctness and reliability of product-related functionalities within the backend system<br>- Supports maintaining high-quality code by validating core operations and behaviors, thereby facilitating robust integration with the overall application architecture<br>- Enhances confidence in product data management and helps prevent regressions during development.</td>
										</tr>
										<tr style='border-bottom: 1px solid #eee;'>
											<td style='padding: 8px;'><b><a href='https://github.com/luizmoretti/Django_ERP/blob/master/BackEnd/apps/inventory/product/views.py'>views.py</a></b></td>
											<td style='padding: 8px;'>- Defines API endpoints for managing product inventory, including listing, creating, retrieving, updating, and deleting products<br>- Facilitates integration with external systems like Home Depot by enabling search and update actions on products<br>- Ensures operations are scoped to the authenticated users company, supporting comprehensive product lifecycle management within the overall inventory architecture.</td>
										</tr>
										<tr style='border-bottom: 1px solid #eee;'>
											<td style='padding: 8px;'><b><a href='https://github.com/luizmoretti/Django_ERP/blob/master/BackEnd/apps/inventory/product/apps.py'>apps.py</a></b></td>
											<td style='padding: 8px;'>- Defines the configuration for the inventory product application within the Django project, establishing its identity and default settings<br>- It integrates the product management module into the overall backend architecture, enabling seamless registration and initialization of product-related functionalities within the inventory system<br>- This setup ensures the application is correctly recognized and managed by Django’s app registry.</td>
										</tr>
										<tr style='border-bottom: 1px solid #eee;'>
											<td style='padding: 8px;'><b><a href='https://github.com/luizmoretti/Django_ERP/blob/master/BackEnd/apps/inventory/product/admin.py'>admin.py</a></b></td>
											<td style='padding: 8px;'>- Defines the administrative interface for managing products and SKUs within the inventory system, enabling streamlined oversight and updates<br>- Facilitates product search and synchronization with external sources like Home Depot, ensuring data accuracy and consistency across the platform<br>- Integrates inline management of store-specific product identifiers for comprehensive inventory control.</td>
										</tr>
										<tr style='border-bottom: 1px solid #eee;'>
											<td style='padding: 8px;'><b><a href='https://github.com/luizmoretti/Django_ERP/blob/master/BackEnd/apps/inventory/product/serializers.py'>serializers.py</a></b></td>
											<td style='padding: 8px;'>- Defines serializers for product-related data, enabling seamless transformation between database models and API responses within the inventory management system<br>- Facilitates creation, update, and retrieval of product details, including associated SKUs, store IDs, and metadata about creators and modifiers, supporting efficient data handling and integration across the backend architecture.</td>
										</tr>
										<tr style='border-bottom: 1px solid #eee;'>
											<td style='padding: 8px;'><b><a href='https://github.com/luizmoretti/Django_ERP/blob/master/BackEnd/apps/inventory/product/models.py'>models.py</a></b></td>
											<td style='padding: 8px;'>- Defines core data models for managing products within the inventory system, including product details, SKUs, and supplier-specific identifiers<br>- Facilitates comprehensive tracking of product attributes, stock levels, and supplier relationships, supporting inventory management, categorization, and supply chain integration across the overall backend architecture.</td>
										</tr>
										<tr style='border-bottom: 1px solid #eee;'>
											<td style='padding: 8px;'><b><a href='https://github.com/luizmoretti/Django_ERP/blob/master/BackEnd/apps/inventory/product/urls.py'>urls.py</a></b></td>
											<td style='padding: 8px;'>- Defines URL routing for product management within the inventory system, enabling operations such as listing, creating, retrieving, updating, and deleting products<br>- Additionally, facilitates specific actions related to Home Depot integrations<br>- This routing setup connects HTTP endpoints to corresponding views, supporting seamless interaction with product data and external actions in the overall backend architecture.</td>
										</tr>
									</table>
									<!-- notifications Submodule -->
									<details>
										<summary><b>notifications</b></summary>
										<blockquote>
											<div class='directory-path' style='padding: 8px 0; color: #666;'>
												<code><b>⦿ BackEnd.apps.inventory.product.notifications</b></code>
											<table style='width: 100%; border-collapse: collapse;'>
											<thead>
												<tr style='background-color: #f8f9fa;'>
													<th style='width: 30%; text-align: left; padding: 8px;'>File Name</th>
													<th style='text-align: left; padding: 8px;'>Summary</th>
												</tr>
											</thead>
												<tr style='border-bottom: 1px solid #eee;'>
													<td style='padding: 8px;'><b><a href='https://github.com/luizmoretti/Django_ERP/blob/master/BackEnd/apps/inventory/product/notifications/constants.py'>constants.py</a></b></td>
													<td style='padding: 8px;'>- Defines constants for the inventory product notification system, including notification types, titles, messages, severity levels, and recipient groups<br>- Facilitates consistent and localized communication about product lifecycle events such as creation, updates, deletions, and attribute changes, ensuring relevant stakeholders receive timely alerts aligned with the applications architecture.</td>
												</tr>
												<tr style='border-bottom: 1px solid #eee;'>
													<td style='padding: 8px;'><b><a href='https://github.com/luizmoretti/Django_ERP/blob/master/BackEnd/apps/inventory/product/notifications/serializers.py'>serializers.py</a></b></td>
													<td style='padding: 8px;'>- Defines serialization logic for product notification data within the inventory management system, enabling consistent data transformation and validation for notification-related operations<br>- Integrates with the broader backend architecture to facilitate seamless communication between the database models and API responses, ensuring accurate and efficient handling of product notification events across the application.</td>
												</tr>
												<tr style='border-bottom: 1px solid #eee;'>
													<td style='padding: 8px;'><b><a href='https://github.com/luizmoretti/Django_ERP/blob/master/BackEnd/apps/inventory/product/notifications/handlers.py'>handlers.py</a></b></td>
													<td style='padding: 8px;'>- Implements a notification handling system for product lifecycle events within the inventory module<br>- It automatically triggers alerts for product creation, updates, and category or brand changes, ensuring relevant stakeholders receive timely, contextual notifications<br>- This component integrates with Django signals to maintain real-time communication, supporting effective monitoring and management of product data changes across the platform.</td>
												</tr>
											</table>
										</blockquote>
									</details>
									<!-- service Submodule -->
									<details>
										<summary><b>service</b></summary>
										<blockquote>
											<div class='directory-path' style='padding: 8px 0; color: #666;'>
												<code><b>⦿ BackEnd.apps.inventory.product.service</b></code>
											<table style='width: 100%; border-collapse: collapse;'>
											<thead>
												<tr style='background-color: #f8f9fa;'>
													<th style='width: 30%; text-align: left; padding: 8px;'>File Name</th>
													<th style='text-align: left; padding: 8px;'>Summary</th>
												</tr>
											</thead>
												<tr style='border-bottom: 1px solid #eee;'>
													<td style='padding: 8px;'><b><a href='https://github.com/luizmoretti/Django_ERP/blob/master/BackEnd/apps/inventory/product/service/home_depot_service.py'>home_depot_service.py</a></b></td>
													<td style='padding: 8px;'>- Provides an interface for interacting with Home Depots product data via the SerpAPI, enabling search and retrieval of detailed product information<br>- Facilitates integration of real-time product availability and pricing into the broader inventory management system, supporting features like product lookup, price comparison, and store-specific queries within the applications architecture.</td>
												</tr>
												<tr style='border-bottom: 1px solid #eee;'>
													<td style='padding: 8px;'><b><a href='https://github.com/luizmoretti/Django_ERP/blob/master/BackEnd/apps/inventory/product/service/product_services.py'>product_services.py</a></b></td>
													<td style='padding: 8px;'>- Provides core services for managing product data within the inventory system, including retrieving product details, associating products with suppliers, and integrating with Home Depot to search, fetch, and update product information<br>- Facilitates synchronization of product attributes like IDs, prices, and descriptions, ensuring accurate and up-to-date inventory data across internal and external sources.</td>
												</tr>
											</table>
										</blockquote>
									</details>
								</blockquote>
							</details>
							<!-- movements Submodule -->
							<details>
								<summary><b>movements</b></summary>
								<blockquote>
									<div class='directory-path' style='padding: 8px 0; color: #666;'>
										<code><b>⦿ BackEnd.apps.inventory.movements</b></code>
									<table style='width: 100%; border-collapse: collapse;'>
									<thead>
										<tr style='background-color: #f8f9fa;'>
											<th style='width: 30%; text-align: left; padding: 8px;'>File Name</th>
											<th style='text-align: left; padding: 8px;'>Summary</th>
										</tr>
									</thead>
										<tr style='border-bottom: 1px solid #eee;'>
											<td style='padding: 8px;'><b><a href='https://github.com/luizmoretti/Django_ERP/blob/master/BackEnd/apps/inventory/movements/tests.py'>tests.py</a></b></td>
											<td style='padding: 8px;'>- Facilitates testing of inventory movement functionalities within the backend system, ensuring the integrity and correctness of inventory operations<br>- Supports validation of business logic related to stock transfers and adjustments, contributing to the overall reliability of inventory management processes in the application architecture.</td>
										</tr>
										<tr style='border-bottom: 1px solid #eee;'>
											<td style='padding: 8px;'><b><a href='https://github.com/luizmoretti/Django_ERP/blob/master/BackEnd/apps/inventory/movements/views.py'>views.py</a></b></td>
											<td style='padding: 8px;'>- Provides an API endpoint to retrieve comprehensive inventory movement records, including inflows, outflows, and transfers<br>- It dynamically filters data based on user roles, offering full visibility for managers and owners, while restricting regular employees to their own activities<br>- Facilitates efficient tracking and auditing of inventory transactions within the systems architecture.</td>
										</tr>
										<tr style='border-bottom: 1px solid #eee;'>
											<td style='padding: 8px;'><b><a href='https://github.com/luizmoretti/Django_ERP/blob/master/BackEnd/apps/inventory/movements/apps.py'>apps.py</a></b></td>
											<td style='padding: 8px;'>- Defines the configuration for the inventory movements module within the backend application, establishing its identity and default settings<br>- It integrates the movements functionality into the overall inventory management architecture, enabling proper registration and initialization of movement-related features in the Django project<br>- This setup ensures seamless inclusion of movement tracking within the broader inventory system.</td>
										</tr>
										<tr style='border-bottom: 1px solid #eee;'>
											<td style='padding: 8px;'><b><a href='https://github.com/luizmoretti/Django_ERP/blob/master/BackEnd/apps/inventory/movements/admin.py'>admin.py</a></b></td>
											<td style='padding: 8px;'>- Defines administrative interface configurations for managing inventory movement records within the backend system<br>- Facilitates streamlined oversight and control of inventory transactions, integrating with Djangos admin framework to enhance data management efficiency across the applications inventory module<br>- This setup supports effective monitoring and administration of inventory movements in the overall architecture.</td>
										</tr>
										<tr style='border-bottom: 1px solid #eee;'>
											<td style='padding: 8px;'><b><a href='https://github.com/luizmoretti/Django_ERP/blob/master/BackEnd/apps/inventory/movements/serializers.py'>serializers.py</a></b></td>
											<td style='padding: 8px;'>- Defines a serializer for inventory movements, standardizing the representation of inflows, outflows, and transfers within the system<br>- It consolidates key movement attributes such as date, type, status, origin, and destination, facilitating consistent data exchange and integration across the backend architecture<br>- This serializer supports clear, structured communication of movement details for inventory tracking and reporting.</td>
										</tr>
										<tr style='border-bottom: 1px solid #eee;'>
											<td style='padding: 8px;'><b><a href='https://github.com/luizmoretti/Django_ERP/blob/master/BackEnd/apps/inventory/movements/models.py'>models.py</a></b></td>
											<td style='padding: 8px;'>- Defines core enumerations for inventory movement types and statuses, facilitating standardized tracking of inventory transactions within the backend architecture<br>- These models enable consistent classification of movements such as entries, exits, and transfers, as well as their current states, supporting reliable inventory management and workflow control across the system.</td>
										</tr>
										<tr style='border-bottom: 1px solid #eee;'>
											<td style='padding: 8px;'><b><a href='https://github.com/luizmoretti/Django_ERP/blob/master/BackEnd/apps/inventory/movements/urls.py'>urls.py</a></b></td>
											<td style='padding: 8px;'>- Defines URL routing for inventory movement endpoints, enabling clients to access a list of all inventory movements within the system<br>- Integrates with the overall backend architecture to facilitate seamless retrieval of movement data, supporting inventory tracking and management functionalities across the application.</td>
										</tr>
									</table>
								</blockquote>
							</details>
							<!-- warehouse Submodule -->
							<details>
								<summary><b>warehouse</b></summary>
								<blockquote>
									<div class='directory-path' style='padding: 8px 0; color: #666;'>
										<code><b>⦿ BackEnd.apps.inventory.warehouse</b></code>
									<table style='width: 100%; border-collapse: collapse;'>
									<thead>
										<tr style='background-color: #f8f9fa;'>
											<th style='width: 30%; text-align: left; padding: 8px;'>File Name</th>
											<th style='text-align: left; padding: 8px;'>Summary</th>
										</tr>
									</thead>
										<tr style='border-bottom: 1px solid #eee;'>
											<td style='padding: 8px;'><b><a href='https://github.com/luizmoretti/Django_ERP/blob/master/BackEnd/apps/inventory/warehouse/tests.py'>tests.py</a></b></td>
											<td style='padding: 8px;'>- Provides comprehensive tests for warehouse inventory management, validating capacity constraints, preventing negative quantities, ensuring transactional integrity, and enforcing warehouse limit adjustments<br>- Ensures robust handling of product quantities within warehouses, safeguarding data consistency and adherence to business rules across inventory operations.</td>
										</tr>
										<tr style='border-bottom: 1px solid #eee;'>
											<td style='padding: 8px;'><b><a href='https://github.com/luizmoretti/Django_ERP/blob/master/BackEnd/apps/inventory/warehouse/views.py'>views.py</a></b></td>
											<td style='padding: 8px;'>- Provides RESTful API endpoints for managing warehouse data within the inventory system, enabling listing, creation, retrieval, updating, and deletion of warehouses<br>- Implements caching strategies to optimize performance and ensures cache invalidation upon data modifications, maintaining data consistency across the architecture<br>- Integrates with user authentication and enforces access control aligned with the overall backend structure.</td>
										</tr>
										<tr style='border-bottom: 1px solid #eee;'>
											<td style='padding: 8px;'><b><a href='https://github.com/luizmoretti/Django_ERP/blob/master/BackEnd/apps/inventory/warehouse/apps.py'>apps.py</a></b></td>
											<td style='padding: 8px;'>- Defines the configuration for the warehouse inventory module within the backend application, establishing its identity and ensuring the automatic import of signal handlers upon application startup<br>- Facilitates seamless integration of event-driven behaviors related to warehouse operations, supporting the overall architecture by enabling responsive and maintainable inventory management processes.</td>
										</tr>
										<tr style='border-bottom: 1px solid #eee;'>
											<td style='padding: 8px;'><b><a href='https://github.com/luizmoretti/Django_ERP/blob/master/BackEnd/apps/inventory/warehouse/admin.py'>admin.py</a></b></td>
											<td style='padding: 8px;'>- Defines administrative interfaces for managing warehouse data within the backend system<br>- Facilitates streamlined creation, editing, and filtering of warehouse records and associated products, ensuring efficient oversight of inventory locations and quantities<br>- Integrates seamlessly into the overall architecture to support inventory management workflows and data consistency across the platform.</td>
										</tr>
										<tr style='border-bottom: 1px solid #eee;'>
											<td style='padding: 8px;'><b><a href='https://github.com/luizmoretti/Django_ERP/blob/master/BackEnd/apps/inventory/warehouse/serializers.py'>serializers.py</a></b></td>
											<td style='padding: 8px;'>- Defines serializers for warehouse and inventory management, enabling structured data validation and transformation within the backend architecture<br>- Facilitates seamless creation, updating, and retrieval of warehouse details and associated products, ensuring data integrity and consistency across the inventory module<br>- Supports the overall systems goal of efficient warehouse operations and inventory tracking.</td>
										</tr>
										<tr style='border-bottom: 1px solid #eee;'>
											<td style='padding: 8px;'><b><a href='https://github.com/luizmoretti/Django_ERP/blob/master/BackEnd/apps/inventory/warehouse/models.py'>models.py</a></b></td>
											<td style='padding: 8px;'>- Defines warehouse and inventory management models, enabling tracking of product quantities, capacity constraints, and location details<br>- Facilitates validation, cache invalidation, and updates of warehouse totals, supporting efficient stock oversight and ensuring data consistency within the broader inventory system architecture.</td>
										</tr>
										<tr style='border-bottom: 1px solid #eee;'>
											<td style='padding: 8px;'><b><a href='https://github.com/luizmoretti/Django_ERP/blob/master/BackEnd/apps/inventory/warehouse/signals.py'>signals.py</a></b></td>
											<td style='padding: 8px;'>- Implements event-driven mechanisms to monitor and enforce warehouse capacity constraints, ensuring data integrity and operational awareness<br>- It tracks changes to warehouse and product quantities, logs capacity warnings, and validates capacity limits before updates, thereby maintaining accurate inventory levels and preventing overcapacity issues within the overall inventory management architecture.</td>
										</tr>
										<tr style='border-bottom: 1px solid #eee;'>
											<td style='padding: 8px;'><b><a href='https://github.com/luizmoretti/Django_ERP/blob/master/BackEnd/apps/inventory/warehouse/urls.py'>urls.py</a></b></td>
											<td style='padding: 8px;'>- Defines URL routing for warehouse management within the inventory system, enabling CRUD operations on warehouse entities<br>- Facilitates seamless interaction between client requests and backend views, supporting efficient creation, retrieval, updating, and deletion of warehouse data as part of the overall inventory architecture.</td>
										</tr>
										<tr style='border-bottom: 1px solid #eee;'>
											<td style='padding: 8px;'><b><a href='https://github.com/luizmoretti/Django_ERP/blob/master/BackEnd/apps/inventory/warehouse/tasks.py'>tasks.py</a></b></td>
											<td style='padding: 8px;'>- Implements background tasks to monitor stock levels across warehouses, identifying products with low inventory and triggering notifications<br>- Ensures proactive inventory management by systematically checking all products or specific items, facilitating timely restocking and maintaining optimal stock levels within the overall warehouse architecture.</td>
										</tr>
									</table>
									<!-- notifications Submodule -->
									<details>
										<summary><b>notifications</b></summary>
										<blockquote>
											<div class='directory-path' style='padding: 8px 0; color: #666;'>
												<code><b>⦿ BackEnd.apps.inventory.warehouse.notifications</b></code>
											<table style='width: 100%; border-collapse: collapse;'>
											<thead>
												<tr style='background-color: #f8f9fa;'>
													<th style='width: 30%; text-align: left; padding: 8px;'>File Name</th>
													<th style='text-align: left; padding: 8px;'>Summary</th>
												</tr>
											</thead>
												<tr style='border-bottom: 1px solid #eee;'>
													<td style='padding: 8px;'><b><a href='https://github.com/luizmoretti/Django_ERP/blob/master/BackEnd/apps/inventory/warehouse/notifications/constants.py'>constants.py</a></b></td>
													<td style='padding: 8px;'>- Defines constants and message templates for warehouse inventory notifications, facilitating standardized alerts on stock levels, replenishments, and adjustments<br>- Supports the entire notification system by categorizing alert types, severities, and localized messages, ensuring consistent communication across the applications inventory management features.</td>
												</tr>
												<tr style='border-bottom: 1px solid #eee;'>
													<td style='padding: 8px;'><b><a href='https://github.com/luizmoretti/Django_ERP/blob/master/BackEnd/apps/inventory/warehouse/notifications/serializers.py'>serializers.py</a></b></td>
													<td style='padding: 8px;'>- Defines serialization logic for warehouse notification data within the inventory management system, enabling consistent data transformation and validation for notifications related to warehouse events<br>- Supports seamless data exchange between backend processes and external interfaces, ensuring reliable communication and integration within the overall inventory architecture.</td>
												</tr>
												<tr style='border-bottom: 1px solid #eee;'>
													<td style='padding: 8px;'><b><a href='https://github.com/luizmoretti/Django_ERP/blob/master/BackEnd/apps/inventory/warehouse/notifications/handlers.py'>handlers.py</a></b></td>
													<td style='padding: 8px;'>- Facilitates warehouse inventory management by handling notifications related to stock levels<br>- It assesses stock severity, alerts stakeholders about low or replenished stock, and ensures timely communication to maintain optimal inventory levels<br>- Integrates with user roles and notification systems to support proactive warehouse operations and inventory oversight within the broader application architecture.</td>
												</tr>
											</table>
										</blockquote>
									</details>
								</blockquote>
							</details>
							<!-- purchase_order Submodule -->
							<details>
								<summary><b>purchase_order</b></summary>
								<blockquote>
									<div class='directory-path' style='padding: 8px 0; color: #666;'>
										<code><b>⦿ BackEnd.apps.inventory.purchase_order</b></code>
									<table style='width: 100%; border-collapse: collapse;'>
									<thead>
										<tr style='background-color: #f8f9fa;'>
											<th style='width: 30%; text-align: left; padding: 8px;'>File Name</th>
											<th style='text-align: left; padding: 8px;'>Summary</th>
										</tr>
									</thead>
										<tr style='border-bottom: 1px solid #eee;'>
											<td style='padding: 8px;'><b><a href='https://github.com/luizmoretti/Django_ERP/blob/master/BackEnd/apps/inventory/purchase_order/tests.py'>tests.py</a></b></td>
											<td style='padding: 8px;'>- The <code>tests.py</code> file in the <code>purchase_order</code> module is designed to validate the core functionality and integrity of the purchase order management system within the backend architecture<br>- It ensures that purchase orders and their associated items are correctly created, retrieved, and manipulated according to the business rules<br>- These tests help maintain data consistency, enforce permissions, and verify the integration of purchase order processes with related entities such as products, suppliers, and users<br>- Overall, this file plays a crucial role in safeguarding the reliability and correctness of the purchase order workflows within the larger inventory management system.</td>
										</tr>
										<tr style='border-bottom: 1px solid #eee;'>
											<td style='padding: 8px;'><b><a href='https://github.com/luizmoretti/Django_ERP/blob/master/BackEnd/apps/inventory/purchase_order/views.py'>views.py</a></b></td>
											<td style='padding: 8px;'>- PurchaseOrder ViewsThis code defines the core API endpoints for managing purchase orders within the backend architecture<br>- It facilitates secure, company-specific access to purchase order data, ensuring that only authenticated users associated with a company can retrieve or manipulate purchase orders<br>- Serving as a foundational component, it integrates with serializers, services, and validators to support the creation, retrieval, and management of purchase orders, thereby enabling seamless procurement workflows across the platform.</td>
										</tr>
										<tr style='border-bottom: 1px solid #eee;'>
											<td style='padding: 8px;'><b><a href='https://github.com/luizmoretti/Django_ERP/blob/master/BackEnd/apps/inventory/purchase_order/apps.py'>apps.py</a></b></td>
											<td style='padding: 8px;'>- Defines the purchase order application within the inventory management system, establishing its configuration and integrating signal handlers and notifications<br>- Facilitates the modular organization of purchase order functionalities, ensuring proper initialization and event handling to support seamless procurement workflows across the platform.</td>
										</tr>
										<tr style='border-bottom: 1px solid #eee;'>
											<td style='padding: 8px;'><b><a href='https://github.com/luizmoretti/Django_ERP/blob/master/BackEnd/apps/inventory/purchase_order/admin.py'>admin.py</a></b></td>
											<td style='padding: 8px;'>- Defines the administrative interface for managing purchase orders and their items within the backend system<br>- Facilitates streamlined creation, editing, and filtering of purchase order records, ensuring efficient oversight of procurement activities<br>- Integrates related purchase order items inline for comprehensive data management, supporting overall inventory and procurement workflows.</td>
										</tr>
										<tr style='border-bottom: 1px solid #eee;'>
											<td style='padding: 8px;'><b><a href='https://github.com/luizmoretti/Django_ERP/blob/master/BackEnd/apps/inventory/purchase_order/serializers.py'>serializers.py</a></b></td>
											<td style='padding: 8px;'>- Defines serializers for managing purchase orders and their items within the inventory system<br>- Facilitates creation, retrieval, and updating of purchase orders, ensuring data validation, transactional integrity, and seamless association with suppliers and products<br>- Supports nested item management, enabling comprehensive handling of purchase order workflows in the backend architecture.</td>
										</tr>
										<tr style='border-bottom: 1px solid #eee;'>
											<td style='padding: 8px;'><b><a href='https://github.com/luizmoretti/Django_ERP/blob/master/BackEnd/apps/inventory/purchase_order/models.py'>models.py</a></b></td>
											<td style='padding: 8px;'>- Defines the data models for managing purchase orders and their items within the inventory system<br>- Facilitates tracking supplier details, order statuses, and total costs, while ensuring data integrity and unique order number generation<br>- Supports seamless creation, updating, and deletion of purchase orders and items, integrating with related product and supplier entities to streamline procurement workflows.</td>
										</tr>
										<tr style='border-bottom: 1px solid #eee;'>
											<td style='padding: 8px;'><b><a href='https://github.com/luizmoretti/Django_ERP/blob/master/BackEnd/apps/inventory/purchase_order/signals.py'>signals.py</a></b></td>
											<td style='padding: 8px;'>- Handles post-save events for purchase orders and items to ensure supplier pricing accuracy and facilitate communication<br>- Updates supplier product prices when purchase order items change, and triggers email notifications to suppliers when purchase orders are created, updated to pending status, or when the first item is added<br>- Supports seamless supplier engagement and data consistency within the inventory management system.</td>
										</tr>
										<tr style='border-bottom: 1px solid #eee;'>
											<td style='padding: 8px;'><b><a href='https://github.com/luizmoretti/Django_ERP/blob/master/BackEnd/apps/inventory/purchase_order/urls.py'>urls.py</a></b></td>
											<td style='padding: 8px;'>- Defines URL routing for purchase order management within the backend architecture, facilitating core operations such as creation, retrieval, updating, deletion, and status actions like approval, rejection, and cancellation<br>- Additionally, it manages purchase order items, enabling addition, updating, and removal, thereby supporting comprehensive lifecycle handling of purchase orders in the system.</td>
										</tr>
									</table>
									<!-- notifications Submodule -->
									<details>
										<summary><b>notifications</b></summary>
										<blockquote>
											<div class='directory-path' style='padding: 8px 0; color: #666;'>
												<code><b>⦿ BackEnd.apps.inventory.purchase_order.notifications</b></code>
											<table style='width: 100%; border-collapse: collapse;'>
											<thead>
												<tr style='background-color: #f8f9fa;'>
													<th style='width: 30%; text-align: left; padding: 8px;'>File Name</th>
													<th style='text-align: left; padding: 8px;'>Summary</th>
												</tr>
											</thead>
												<tr style='border-bottom: 1px solid #eee;'>
													<td style='padding: 8px;'><b><a href='https://github.com/luizmoretti/Django_ERP/blob/master/BackEnd/apps/inventory/purchase_order/notifications/constants.py'>constants.py</a></b></td>
													<td style='padding: 8px;'>- Defines constants for purchase order notifications, including types, titles, messages, severity levels, and recipient groups<br>- Facilitates consistent, localized communication across the inventory management system by standardizing notification content and delivery parameters related to purchase order events<br>- Supports clear, structured alerts to relevant stakeholders, enhancing operational awareness and response.</td>
												</tr>
												<tr style='border-bottom: 1px solid #eee;'>
													<td style='padding: 8px;'><b><a href='https://github.com/luizmoretti/Django_ERP/blob/master/BackEnd/apps/inventory/purchase_order/notifications/handlers.py'>handlers.py</a></b></td>
													<td style='padding: 8px;'>- Implements event-driven notifications for purchase order lifecycle events, including creation, updates, status changes, item modifications, and deletions<br>- Ensures stakeholders receive timely alerts, maintains synchronization during deletions, and tracks changes to facilitate proactive communication within the inventory management architecture.</td>
												</tr>
											</table>
										</blockquote>
									</details>
									<!-- services Submodule -->
									<details>
										<summary><b>services</b></summary>
										<blockquote>
											<div class='directory-path' style='padding: 8px 0; color: #666;'>
												<code><b>⦿ BackEnd.apps.inventory.purchase_order.services</b></code>
											<table style='width: 100%; border-collapse: collapse;'>
											<thead>
												<tr style='background-color: #f8f9fa;'>
													<th style='width: 30%; text-align: left; padding: 8px;'>File Name</th>
													<th style='text-align: left; padding: 8px;'>Summary</th>
												</tr>
											</thead>
												<tr style='border-bottom: 1px solid #eee;'>
													<td style='padding: 8px;'><b><a href='https://github.com/luizmoretti/Django_ERP/blob/master/BackEnd/apps/inventory/purchase_order/services/reports.py'>reports.py</a></b></td>
													<td style='padding: 8px;'>- Generate comprehensive purchase order reports to facilitate inventory management and decision-making<br>- The module consolidates data insights related to purchase activities, enabling users to analyze trends, track order statuses, and optimize procurement processes within the broader inventory system<br>- It plays a crucial role in ensuring accurate, timely reporting for effective supply chain oversight.</td>
												</tr>
												<tr style='border-bottom: 1px solid #eee;'>
													<td style='padding: 8px;'><b><a href='https://github.com/luizmoretti/Django_ERP/blob/master/BackEnd/apps/inventory/purchase_order/services/handlers.py'>handlers.py</a></b></td>
													<td style='padding: 8px;'>- Provides core business logic for managing purchase orders and their items within the backend architecture<br>- Facilitates order lifecycle operations such as approval, rejection, and cancellation, while ensuring data integrity and permission validation<br>- Also handles item addition, updates, removal, and change detection, supporting seamless and consistent purchase order workflows across the system.</td>
												</tr>
												<tr style='border-bottom: 1px solid #eee;'>
													<td style='padding: 8px;'><b><a href='https://github.com/luizmoretti/Django_ERP/blob/master/BackEnd/apps/inventory/purchase_order/services/validators.py'>validators.py</a></b></td>
													<td style='padding: 8px;'>- Provides comprehensive validation logic for purchase order workflows, ensuring data integrity, proper status transitions, and permission enforcement<br>- Facilitates reliable creation, modification, and management of purchase orders and their items within the system, supporting consistent business rules and safeguarding against invalid operations across the entire inventory management architecture.</td>
												</tr>
											</table>
										</blockquote>
									</details>
								</blockquote>
							</details>
							<!-- supplier Submodule -->
							<details>
								<summary><b>supplier</b></summary>
								<blockquote>
									<div class='directory-path' style='padding: 8px 0; color: #666;'>
										<code><b>⦿ BackEnd.apps.inventory.supplier</b></code>
									<table style='width: 100%; border-collapse: collapse;'>
									<thead>
										<tr style='background-color: #f8f9fa;'>
											<th style='width: 30%; text-align: left; padding: 8px;'>File Name</th>
											<th style='text-align: left; padding: 8px;'>Summary</th>
										</tr>
									</thead>
										<tr style='border-bottom: 1px solid #eee;'>
											<td style='padding: 8px;'><b><a href='https://github.com/luizmoretti/Django_ERP/blob/master/BackEnd/apps/inventory/supplier/tests.py'>tests.py</a></b></td>
											<td style='padding: 8px;'>- Provides unit tests for the supplier management functionalities within the inventory application, ensuring the reliability and correctness of supplier-related features<br>- Supports the overall architecture by validating business logic and data integrity, facilitating maintainability and robustness of the backend system in managing supplier information.</td>
										</tr>
										<tr style='border-bottom: 1px solid #eee;'>
											<td style='padding: 8px;'><b><a href='https://github.com/luizmoretti/Django_ERP/blob/master/BackEnd/apps/inventory/supplier/views.py'>views.py</a></b></td>
											<td style='padding: 8px;'>- Defines API endpoints for managing supplier data within the inventory system, enabling listing, creation, retrieval, updating, and deletion of suppliers<br>- Ensures operations are scoped to the authenticated users company, maintains consistent permission enforcement, and integrates detailed schema documentation for seamless API understanding and usage<br>- Facilitates efficient supplier management aligned with the overall inventory architecture.</td>
										</tr>
										<tr style='border-bottom: 1px solid #eee;'>
											<td style='padding: 8px;'><b><a href='https://github.com/luizmoretti/Django_ERP/blob/master/BackEnd/apps/inventory/supplier/apps.py'>apps.py</a></b></td>
											<td style='padding: 8px;'>- Defines the configuration for the supplier management module within the inventory system, establishing its integration point in the Django project architecture<br>- It facilitates the registration and setup of supplier-related functionalities, ensuring seamless inclusion of supplier data handling and operations within the overall backend framework.</td>
										</tr>
										<tr style='border-bottom: 1px solid #eee;'>
											<td style='padding: 8px;'><b><a href='https://github.com/luizmoretti/Django_ERP/blob/master/BackEnd/apps/inventory/supplier/admin.py'>admin.py</a></b></td>
											<td style='padding: 8px;'>- Defines the administrative interface for managing supplier records within the inventory module, enabling streamlined oversight of supplier details<br>- It facilitates efficient data handling by customizing display options, filters, and search capabilities, ensuring accurate and accessible supplier information management aligned with the overall backend architecture.</td>
										</tr>
										<tr style='border-bottom: 1px solid #eee;'>
											<td style='padding: 8px;'><b><a href='https://github.com/luizmoretti/Django_ERP/blob/master/BackEnd/apps/inventory/supplier/serializers.py'>serializers.py</a></b></td>
											<td style='padding: 8px;'>- Defines serializers for managing supplier data and their product pricing within the inventory system<br>- Facilitates structured data exchange for supplier details, associated product prices, and metadata such as creator, updater, and company information<br>- Supports seamless integration between the backend models and API responses, ensuring consistent and comprehensive representation of supplier-related information across the application.</td>
										</tr>
										<tr style='border-bottom: 1px solid #eee;'>
											<td style='padding: 8px;'><b><a href='https://github.com/luizmoretti/Django_ERP/blob/master/BackEnd/apps/inventory/supplier/models.py'>models.py</a></b></td>
											<td style='padding: 8px;'>- Defines core models for managing suppliers and their product pricing within the inventory system<br>- Facilitates tracking supplier details, addresses, and historical price data, enabling efficient supplier relationship management and accurate pricing updates across the platform<br>- Integrates seamlessly with product and company data to support comprehensive supply chain operations.</td>
										</tr>
										<tr style='border-bottom: 1px solid #eee;'>
											<td style='padding: 8px;'><b><a href='https://github.com/luizmoretti/Django_ERP/blob/master/BackEnd/apps/inventory/supplier/signals.py'>signals.py</a></b></td>
											<td style='padding: 8px;'>- Facilitates automatic event handling and data synchronization related to supplier activities within the inventory management system<br>- It ensures that relevant signals trigger appropriate responses, maintaining data consistency and integrity across the backend architecture<br>- This component plays a crucial role in streamlining supplier-related workflows and supporting real-time updates within the overall inventory ecosystem.</td>
										</tr>
										<tr style='border-bottom: 1px solid #eee;'>
											<td style='padding: 8px;'><b><a href='https://github.com/luizmoretti/Django_ERP/blob/master/BackEnd/apps/inventory/supplier/urls.py'>urls.py</a></b></td>
											<td style='padding: 8px;'>- Defines URL routing for supplier management within the inventory module, enabling CRUD operations<br>- It facilitates seamless interaction with supplier data by mapping HTTP endpoints to corresponding views, supporting efficient supplier data handling and integration within the broader inventory system architecture.</td>
										</tr>
									</table>
									<!-- notifications Submodule -->
									<details>
										<summary><b>notifications</b></summary>
										<blockquote>
											<div class='directory-path' style='padding: 8px 0; color: #666;'>
												<code><b>⦿ BackEnd.apps.inventory.supplier.notifications</b></code>
											<table style='width: 100%; border-collapse: collapse;'>
											<thead>
												<tr style='background-color: #f8f9fa;'>
													<th style='width: 30%; text-align: left; padding: 8px;'>File Name</th>
													<th style='text-align: left; padding: 8px;'>Summary</th>
												</tr>
											</thead>
												<tr style='border-bottom: 1px solid #eee;'>
													<td style='padding: 8px;'><b><a href='https://github.com/luizmoretti/Django_ERP/blob/master/BackEnd/apps/inventory/supplier/notifications/constants.py'>constants.py</a></b></td>
													<td style='padding: 8px;'>- Define standardized notification constants for supplier-related events within the inventory management system, ensuring consistent messaging and event handling across the backend application<br>- These constants facilitate clear communication and streamlined processing of supplier notifications, supporting the overall architectures goal of reliable and maintainable inventory operations.</td>
												</tr>
												<tr style='border-bottom: 1px solid #eee;'>
													<td style='padding: 8px;'><b><a href='https://github.com/luizmoretti/Django_ERP/blob/master/BackEnd/apps/inventory/supplier/notifications/serializers.py'>serializers.py</a></b></td>
													<td style='padding: 8px;'>- Defines serialization logic for supplier notification data within the inventory management system, enabling seamless conversion between complex data structures and formats suitable for API communication<br>- Facilitates consistent data handling and validation for supplier notifications, ensuring reliable integration and data exchange across the backend applications inventory module.</td>
												</tr>
												<tr style='border-bottom: 1px solid #eee;'>
													<td style='padding: 8px;'><b><a href='https://github.com/luizmoretti/Django_ERP/blob/master/BackEnd/apps/inventory/supplier/notifications/handlers.py'>handlers.py</a></b></td>
													<td style='padding: 8px;'>- Facilitates the management and dispatch of supplier notification events within the inventory system, ensuring timely communication and updates<br>- Integrates with the broader backend architecture to support real-time alerts and automated messaging, thereby enhancing supplier engagement and operational efficiency across the inventory management workflow.</td>
												</tr>
											</table>
										</blockquote>
									</details>
									<!-- services Submodule -->
									<details>
										<summary><b>services</b></summary>
										<blockquote>
											<div class='directory-path' style='padding: 8px 0; color: #666;'>
												<code><b>⦿ BackEnd.apps.inventory.supplier.services</b></code>
											<table style='width: 100%; border-collapse: collapse;'>
											<thead>
												<tr style='background-color: #f8f9fa;'>
													<th style='width: 30%; text-align: left; padding: 8px;'>File Name</th>
													<th style='text-align: left; padding: 8px;'>Summary</th>
												</tr>
											</thead>
												<tr style='border-bottom: 1px solid #eee;'>
													<td style='padding: 8px;'><b><a href='https://github.com/luizmoretti/Django_ERP/blob/master/BackEnd/apps/inventory/supplier/services/reports.py'>reports.py</a></b></td>
													<td style='padding: 8px;'>- Generate comprehensive supplier reports to facilitate inventory management and decision-making<br>- The code consolidates supplier data, analyzes trends, and produces structured insights, integrating seamlessly within the backend inventory system to support efficient supplier evaluation and inventory planning.</td>
												</tr>
												<tr style='border-bottom: 1px solid #eee;'>
													<td style='padding: 8px;'><b><a href='https://github.com/luizmoretti/Django_ERP/blob/master/BackEnd/apps/inventory/supplier/services/handlers.py'>handlers.py</a></b></td>
													<td style='padding: 8px;'>- Facilitates supplier-related operations within the inventory management system by handling core business logic and service interactions<br>- Integrates supplier data workflows to ensure seamless communication between the applications core components and external supplier systems, supporting efficient inventory updates, supplier management, and data consistency across the backend architecture.</td>
												</tr>
												<tr style='border-bottom: 1px solid #eee;'>
													<td style='padding: 8px;'><b><a href='https://github.com/luizmoretti/Django_ERP/blob/master/BackEnd/apps/inventory/supplier/services/validators.py'>validators.py</a></b></td>
													<td style='padding: 8px;'>- Provides validation logic for supplier-related data within the inventory management system, ensuring data integrity and consistency before processing or storage<br>- Integrates with the broader backend architecture to enforce business rules and maintain reliable supplier information, supporting seamless inventory operations and accurate supplier records across the application.</td>
												</tr>
											</table>
										</blockquote>
									</details>
								</blockquote>
							</details>
							<!-- brand Submodule -->
							<details>
								<summary><b>brand</b></summary>
								<blockquote>
									<div class='directory-path' style='padding: 8px 0; color: #666;'>
										<code><b>⦿ BackEnd.apps.inventory.brand</b></code>
									<table style='width: 100%; border-collapse: collapse;'>
									<thead>
										<tr style='background-color: #f8f9fa;'>
											<th style='width: 30%; text-align: left; padding: 8px;'>File Name</th>
											<th style='text-align: left; padding: 8px;'>Summary</th>
										</tr>
									</thead>
										<tr style='border-bottom: 1px solid #eee;'>
											<td style='padding: 8px;'><b><a href='https://github.com/luizmoretti/Django_ERP/blob/master/BackEnd/apps/inventory/brand/tests.py'>tests.py</a></b></td>
											<td style='padding: 8px;'>- Provides test cases for the inventory brand management module, ensuring the correctness and reliability of brand-related functionalities within the backend system<br>- Supports maintaining data integrity and robustness in the overall inventory architecture by validating brand operations and interactions in the Django application.</td>
										</tr>
										<tr style='border-bottom: 1px solid #eee;'>
											<td style='padding: 8px;'><b><a href='https://github.com/luizmoretti/Django_ERP/blob/master/BackEnd/apps/inventory/brand/views.py'>views.py</a></b></td>
											<td style='padding: 8px;'>- Defines API endpoints for managing brands within the inventory system, enabling listing, creation, retrieval, updating, and deletion of brand records<br>- Ensures operations are scoped to the authenticated users associated company and enforces permission checks<br>- Facilitates seamless integration of brand data management into the broader inventory architecture, supporting efficient and secure brand lifecycle handling.</td>
										</tr>
										<tr style='border-bottom: 1px solid #eee;'>
											<td style='padding: 8px;'><b><a href='https://github.com/luizmoretti/Django_ERP/blob/master/BackEnd/apps/inventory/brand/apps.py'>apps.py</a></b></td>
											<td style='padding: 8px;'>- Defines the application configuration for the brand management module within the inventory system, establishing its identity and default settings<br>- It integrates the brand component into the overall backend architecture, enabling organized handling of brand-related data and operations within the larger inventory management framework.</td>
										</tr>
										<tr style='border-bottom: 1px solid #eee;'>
											<td style='padding: 8px;'><b><a href='https://github.com/luizmoretti/Django_ERP/blob/master/BackEnd/apps/inventory/brand/admin.py'>admin.py</a></b></td>
											<td style='padding: 8px;'>- Defines the administrative interface for managing brand entities within the inventory module, enabling efficient oversight of brand details, creation, and modification history<br>- Facilitates filtering, searching, and display customization to streamline backend operations and ensure accurate, accessible brand data management across the platform.</td>
										</tr>
										<tr style='border-bottom: 1px solid #eee;'>
											<td style='padding: 8px;'><b><a href='https://github.com/luizmoretti/Django_ERP/blob/master/BackEnd/apps/inventory/brand/serializers.py'>serializers.py</a></b></td>
											<td style='padding: 8px;'>- Defines serialization logic for Brand entities within the inventory module, facilitating data transformation between database models and API responses<br>- Ensures consistent formatting and inclusion of related company and user information, supporting seamless data exchange and integrity across the backend architecture<br>- Enhances the APIs ability to present comprehensive brand details while maintaining data validation and integrity.</td>
										</tr>
										<tr style='border-bottom: 1px solid #eee;'>
											<td style='padding: 8px;'><b><a href='https://github.com/luizmoretti/Django_ERP/blob/master/BackEnd/apps/inventory/brand/models.py'>models.py</a></b></td>
											<td style='padding: 8px;'>- Defines the Brand model within the inventory management system, representing product brands associated with companies<br>- It facilitates the organization and retrieval of brand-related data, supporting features like brand categorization and sorting<br>- As part of the backend architecture, it integrates with other models to enable comprehensive inventory tracking and management across multiple companies.</td>
										</tr>
										<tr style='border-bottom: 1px solid #eee;'>
											<td style='padding: 8px;'><b><a href='https://github.com/luizmoretti/Django_ERP/blob/master/BackEnd/apps/inventory/brand/urls.py'>urls.py</a></b></td>
											<td style='padding: 8px;'>- Defines URL endpoints for managing brand entities within the inventory module, enabling clients to perform CRUD operations<br>- Integrates with view classes to facilitate listing, creating, retrieving, updating, and deleting brand records, thereby supporting the broader inventory management architecture by providing a structured interface for brand data manipulation.</td>
										</tr>
									</table>
									<!-- notifications Submodule -->
									<details>
										<summary><b>notifications</b></summary>
										<blockquote>
											<div class='directory-path' style='padding: 8px 0; color: #666;'>
												<code><b>⦿ BackEnd.apps.inventory.brand.notifications</b></code>
											<table style='width: 100%; border-collapse: collapse;'>
											<thead>
												<tr style='background-color: #f8f9fa;'>
													<th style='width: 30%; text-align: left; padding: 8px;'>File Name</th>
													<th style='text-align: left; padding: 8px;'>Summary</th>
												</tr>
											</thead>
												<tr style='border-bottom: 1px solid #eee;'>
													<td style='padding: 8px;'><b><a href='https://github.com/luizmoretti/Django_ERP/blob/master/BackEnd/apps/inventory/brand/notifications/constants.py'>constants.py</a></b></td>
													<td style='padding: 8px;'>- Define notification-related constants for the inventory brand module, facilitating consistent messaging and event handling across the backend system<br>- These constants support the broader architecture by standardizing notification parameters, ensuring reliable communication and integration within the inventory management ecosystem.</td>
												</tr>
												<tr style='border-bottom: 1px solid #eee;'>
													<td style='padding: 8px;'><b><a href='https://github.com/luizmoretti/Django_ERP/blob/master/BackEnd/apps/inventory/brand/notifications/serializers.py'>serializers.py</a></b></td>
													<td style='padding: 8px;'>- Defines serialization logic for brand notification data within the inventory applications backend, facilitating seamless data transformation between internal models and external representations<br>- Supports consistent communication and data exchange related to brand notifications, ensuring integration with other system components and external services operate smoothly within the overall inventory management architecture.</td>
												</tr>
												<tr style='border-bottom: 1px solid #eee;'>
													<td style='padding: 8px;'><b><a href='https://github.com/luizmoretti/Django_ERP/blob/master/BackEnd/apps/inventory/brand/notifications/handlers.py'>handlers.py</a></b></td>
													<td style='padding: 8px;'>- Facilitates the management and dispatch of notification events related to brand inventory updates within the backend architecture<br>- Integrates with the broader notification system to ensure timely alerts and consistent communication for inventory changes, supporting seamless coordination across the inventory management module and enhancing real-time responsiveness across the platform.</td>
												</tr>
											</table>
										</blockquote>
									</details>
								</blockquote>
							</details>
							<!-- categories Submodule -->
							<details>
								<summary><b>categories</b></summary>
								<blockquote>
									<div class='directory-path' style='padding: 8px 0; color: #666;'>
										<code><b>⦿ BackEnd.apps.inventory.categories</b></code>
									<table style='width: 100%; border-collapse: collapse;'>
									<thead>
										<tr style='background-color: #f8f9fa;'>
											<th style='width: 30%; text-align: left; padding: 8px;'>File Name</th>
											<th style='text-align: left; padding: 8px;'>Summary</th>
										</tr>
									</thead>
										<tr style='border-bottom: 1px solid #eee;'>
											<td style='padding: 8px;'><b><a href='https://github.com/luizmoretti/Django_ERP/blob/master/BackEnd/apps/inventory/categories/tests.py'>tests.py</a></b></td>
											<td style='padding: 8px;'>- Provides test cases for the inventory categories module, ensuring the correctness and reliability of category-related functionalities within the backend system<br>- Supports maintaining data integrity and expected behavior in the inventory management architecture by validating category operations through automated tests.</td>
										</tr>
										<tr style='border-bottom: 1px solid #eee;'>
											<td style='padding: 8px;'><b><a href='https://github.com/luizmoretti/Django_ERP/blob/master/BackEnd/apps/inventory/categories/views.py'>views.py</a></b></td>
											<td style='padding: 8px;'>- Defines the API endpoints for managing inventory categories within the backend application, facilitating the creation, retrieval, updating, and deletion of category data<br>- Integrates with the overall architecture to support organized classification of inventory items, enabling efficient data handling and interaction for frontend components and other services.</td>
										</tr>
										<tr style='border-bottom: 1px solid #eee;'>
											<td style='padding: 8px;'><b><a href='https://github.com/luizmoretti/Django_ERP/blob/master/BackEnd/apps/inventory/categories/apps.py'>apps.py</a></b></td>
											<td style='padding: 8px;'>- Defines the configuration for the categories module within the inventory app, establishing its identity and default database auto-incrementing behavior<br>- It integrates the categories component into the overall inventory architecture, enabling Django to recognize and manage category-related data models effectively<br>- This setup facilitates organized categorization and streamlined data handling across the inventory system.</td>
										</tr>
										<tr style='border-bottom: 1px solid #eee;'>
											<td style='padding: 8px;'><b><a href='https://github.com/luizmoretti/Django_ERP/blob/master/BackEnd/apps/inventory/categories/admin.py'>admin.py</a></b></td>
											<td style='padding: 8px;'>- Defines administrative interface for managing inventory categories within the backend system, enabling efficient oversight of category data<br>- Facilitates viewing, filtering, and searching categories, while providing clear attribution of creation and modification details<br>- Integrates seamlessly into the overall architecture to support inventory organization and administrative workflows.</td>
										</tr>
										<tr style='border-bottom: 1px solid #eee;'>
											<td style='padding: 8px;'><b><a href='https://github.com/luizmoretti/Django_ERP/blob/master/BackEnd/apps/inventory/categories/serializers.py'>serializers.py</a></b></td>
											<td style='padding: 8px;'>- Defines serialization logic for inventory category data, enabling seamless conversion between complex data structures and formats suitable for API communication<br>- Facilitates consistent data representation and validation within the inventory management system, supporting efficient data exchange and integration across the backend architecture<br>- Ensures that category-related information is accurately processed and transmitted throughout the application.</td>
										</tr>
										<tr style='border-bottom: 1px solid #eee;'>
											<td style='padding: 8px;'><b><a href='https://github.com/luizmoretti/Django_ERP/blob/master/BackEnd/apps/inventory/categories/models.py'>models.py</a></b></td>
											<td style='padding: 8px;'>- Defines the Category model within the inventory management system, enabling classification of inventory items<br>- It extends a base model to include essential metadata and relationships, facilitating organized categorization and efficient retrieval of inventory data<br>- This component plays a crucial role in structuring inventory data hierarchically within the overall backend architecture.</td>
										</tr>
										<tr style='border-bottom: 1px solid #eee;'>
											<td style='padding: 8px;'><b><a href='https://github.com/luizmoretti/Django_ERP/blob/master/BackEnd/apps/inventory/categories/urls.py'>urls.py</a></b></td>
											<td style='padding: 8px;'>- Defines URL routing for inventory category management, enabling seamless API endpoints for creating, retrieving, updating, and deleting categories within the backend architecture<br>- Facilitates organized access to category data, supporting efficient inventory classification and integration with other system components in the overall project structure.</td>
										</tr>
									</table>
									<!-- notifications Submodule -->
									<details>
										<summary><b>notifications</b></summary>
										<blockquote>
											<div class='directory-path' style='padding: 8px 0; color: #666;'>
												<code><b>⦿ BackEnd.apps.inventory.categories.notifications</b></code>
											<table style='width: 100%; border-collapse: collapse;'>
											<thead>
												<tr style='background-color: #f8f9fa;'>
													<th style='width: 30%; text-align: left; padding: 8px;'>File Name</th>
													<th style='text-align: left; padding: 8px;'>Summary</th>
												</tr>
											</thead>
												<tr style='border-bottom: 1px solid #eee;'>
													<td style='padding: 8px;'><b><a href='https://github.com/luizmoretti/Django_ERP/blob/master/BackEnd/apps/inventory/categories/notifications/constants.py'>constants.py</a></b></td>
													<td style='padding: 8px;'>- Defines constant values used for notification handling within the inventory categories module, supporting consistent messaging and event triggers across the backend system<br>- Facilitates streamlined communication processes related to inventory category updates and alerts, ensuring uniformity and ease of maintenance within the overall backend architecture.</td>
												</tr>
												<tr style='border-bottom: 1px solid #eee;'>
													<td style='padding: 8px;'><b><a href='https://github.com/luizmoretti/Django_ERP/blob/master/BackEnd/apps/inventory/categories/notifications/serializers.py'>serializers.py</a></b></td>
													<td style='padding: 8px;'>- Defines serialization logic for inventory category notifications, enabling consistent data transformation and validation within the backend application<br>- Facilitates seamless communication between the database models and API responses, ensuring accurate and structured notification data handling across the inventory management system<br>- Supports reliable notification processing and integration within the broader backend architecture.</td>
												</tr>
												<tr style='border-bottom: 1px solid #eee;'>
													<td style='padding: 8px;'><b><a href='https://github.com/luizmoretti/Django_ERP/blob/master/BackEnd/apps/inventory/categories/notifications/handlers.py'>handlers.py</a></b></td>
													<td style='padding: 8px;'>- Facilitates the management and dispatch of notifications related to inventory category events within the backend system<br>- Integrates with the broader notification framework to ensure timely updates and alerts, supporting seamless communication across inventory management processes<br>- Enhances the system’s responsiveness by handling category-specific notifications, contributing to efficient inventory oversight and user awareness.</td>
												</tr>
											</table>
										</blockquote>
									</details>
								</blockquote>
							</details>
							<!-- transfer Submodule -->
							<details>
								<summary><b>transfer</b></summary>
								<blockquote>
									<div class='directory-path' style='padding: 8px 0; color: #666;'>
										<code><b>⦿ BackEnd.apps.inventory.transfer</b></code>
									<table style='width: 100%; border-collapse: collapse;'>
									<thead>
										<tr style='background-color: #f8f9fa;'>
											<th style='width: 30%; text-align: left; padding: 8px;'>File Name</th>
											<th style='text-align: left; padding: 8px;'>Summary</th>
										</tr>
									</thead>
										<tr style='border-bottom: 1px solid #eee;'>
											<td style='padding: 8px;'><b><a href='https://github.com/luizmoretti/Django_ERP/blob/master/BackEnd/apps/inventory/transfer/tests.py'>tests.py</a></b></td>
											<td style='padding: 8px;'>- Facilitates comprehensive testing of warehouse transfer operations, ensuring inventory quantities are accurately updated, validated against warehouse limits, and properly handled during creation, updates, and deletions<br>- Validates capacity constraints, manages unlimited warehouses, and verifies system warnings, thereby maintaining inventory integrity and supporting reliable transfer workflows within the overall supply chain architecture.</td>
										</tr>
										<tr style='border-bottom: 1px solid #eee;'>
											<td style='padding: 8px;'><b><a href='https://github.com/luizmoretti/Django_ERP/blob/master/BackEnd/apps/inventory/transfer/views.py'>views.py</a></b></td>
											<td style='padding: 8px;'>- Defines API endpoints for managing inventory transfers, enabling listing, creation, retrieval, updating, and deletion of transfer records<br>- Integrates user authentication and validation to ensure secure and accurate transfer operations within the inventory system, supporting seamless transfer lifecycle management aligned with the overall backend architecture.</td>
										</tr>
										<tr style='border-bottom: 1px solid #eee;'>
											<td style='padding: 8px;'><b><a href='https://github.com/luizmoretti/Django_ERP/blob/master/BackEnd/apps/inventory/transfer/apps.py'>apps.py</a></b></td>
											<td style='padding: 8px;'>- Defines the application configuration for the inventory transfer module within the backend, establishing its identity and ensuring the automatic registration of signal handlers upon startup<br>- Integrates the transfer functionality into the overall inventory management architecture, facilitating seamless transfer processes and event-driven responses across the system.</td>
										</tr>
										<tr style='border-bottom: 1px solid #eee;'>
											<td style='padding: 8px;'><b><a href='https://github.com/luizmoretti/Django_ERP/blob/master/BackEnd/apps/inventory/transfer/admin.py'>admin.py</a></b></td>
											<td style='padding: 8px;'>- Defines administrative interface for managing inventory transfers, enabling streamlined oversight of transfer records and associated items<br>- Facilitates efficient creation, editing, and filtering of transfer data within the backend, ensuring accurate tracking of inventory movements across locations<br>- Integrates inline management of transfer items, supporting comprehensive and user-friendly inventory transfer operations within the overall system architecture.</td>
										</tr>
										<tr style='border-bottom: 1px solid #eee;'>
											<td style='padding: 8px;'><b><a href='https://github.com/luizmoretti/Django_ERP/blob/master/BackEnd/apps/inventory/transfer/serializers.py'>serializers.py</a></b></td>
											<td style='padding: 8px;'>- Defines serialization logic for inventory transfer operations, enabling creation, validation, and updating of transfer records along with their associated items<br>- Facilitates seamless data exchange between the application and external interfaces, ensuring transfer details are accurately captured, validated, and persisted within the broader warehouse management architecture.</td>
										</tr>
										<tr style='border-bottom: 1px solid #eee;'>
											<td style='padding: 8px;'><b><a href='https://github.com/luizmoretti/Django_ERP/blob/master/BackEnd/apps/inventory/transfer/models.py'>models.py</a></b></td>
											<td style='padding: 8px;'>- Defines the data models for managing inventory transfers between warehouses, capturing transfer details, statuses, and associated products<br>- Facilitates tracking of transfer origins, destinations, and item quantities, supporting seamless inventory movement within the broader warehouse management architecture<br>- These models enable efficient recording, status updates, and auditing of transfer activities across the system.</td>
										</tr>
										<tr style='border-bottom: 1px solid #eee;'>
											<td style='padding: 8px;'><b><a href='https://github.com/luizmoretti/Django_ERP/blob/master/BackEnd/apps/inventory/transfer/signals.py'>signals.py</a></b></td>
											<td style='padding: 8px;'>- Implements signal handlers to enforce inventory transfer integrity by validating quantities, updating warehouse stock levels, and maintaining consistency during creation, updates, or deletion of transfer items<br>- Ensures warehouse capacity limits are respected, prevents negative stock levels, and automates stock adjustments to support accurate inventory management across warehouses.</td>
										</tr>
										<tr style='border-bottom: 1px solid #eee;'>
											<td style='padding: 8px;'><b><a href='https://github.com/luizmoretti/Django_ERP/blob/master/BackEnd/apps/inventory/transfer/urls.py'>urls.py</a></b></td>
											<td style='padding: 8px;'>- Defines URL routing for inventory transfer operations within the backend, enabling clients to list, create, retrieve, update, and delete transfer records<br>- Serves as the central navigation point for transfer-related API endpoints, facilitating seamless interaction with transfer data and supporting inventory management workflows in the overall system architecture.</td>
										</tr>
									</table>
									<!-- notifications Submodule -->
									<details>
										<summary><b>notifications</b></summary>
										<blockquote>
											<div class='directory-path' style='padding: 8px 0; color: #666;'>
												<code><b>⦿ BackEnd.apps.inventory.transfer.notifications</b></code>
											<table style='width: 100%; border-collapse: collapse;'>
											<thead>
												<tr style='background-color: #f8f9fa;'>
													<th style='width: 30%; text-align: left; padding: 8px;'>File Name</th>
													<th style='text-align: left; padding: 8px;'>Summary</th>
												</tr>
											</thead>
												<tr style='border-bottom: 1px solid #eee;'>
													<td style='padding: 8px;'><b><a href='https://github.com/luizmoretti/Django_ERP/blob/master/BackEnd/apps/inventory/transfer/notifications/constants.py'>constants.py</a></b></td>
													<td style='padding: 8px;'>- Defines notification constants for transfer-related events within the inventory management system, facilitating consistent messaging and severity levels<br>- Supports user-specific notification targeting across roles such as stock controllers, managers, and executives, ensuring clear communication of transfer statuses like creation, approval, rejection, cancellation, and completion across the applications architecture.</td>
												</tr>
												<tr style='border-bottom: 1px solid #eee;'>
													<td style='padding: 8px;'><b><a href='https://github.com/luizmoretti/Django_ERP/blob/master/BackEnd/apps/inventory/transfer/notifications/serializers.py'>serializers.py</a></b></td>
													<td style='padding: 8px;'>- Defines serialization logic for transfer notification data within the inventory management system, enabling consistent data formatting and validation for transfer-related notifications<br>- Integrates with the broader backend architecture to facilitate seamless communication and data exchange related to inventory transfers, ensuring reliable and structured notification handling across the application.</td>
												</tr>
												<tr style='border-bottom: 1px solid #eee;'>
													<td style='padding: 8px;'><b><a href='https://github.com/luizmoretti/Django_ERP/blob/master/BackEnd/apps/inventory/transfer/notifications/handlers.py'>handlers.py</a></b></td>
													<td style='padding: 8px;'>- Facilitates automated notifications related to transfer lifecycle events within the inventory system<br>- It ensures stakeholders are informed of transfer creation, approval, rejection, and completion, enhancing operational transparency and communication<br>- The handler manages message composition, recipient targeting, and integrates seamlessly with Django signals to trigger notifications upon relevant transfer model changes.</td>
												</tr>
											</table>
										</blockquote>
									</details>
									<!-- services Submodule -->
									<details>
										<summary><b>services</b></summary>
										<blockquote>
											<div class='directory-path' style='padding: 8px 0; color: #666;'>
												<code><b>⦿ BackEnd.apps.inventory.transfer.services</b></code>
											<table style='width: 100%; border-collapse: collapse;'>
											<thead>
												<tr style='background-color: #f8f9fa;'>
													<th style='width: 30%; text-align: left; padding: 8px;'>File Name</th>
													<th style='text-align: left; padding: 8px;'>Summary</th>
												</tr>
											</thead>
												<tr style='border-bottom: 1px solid #eee;'>
													<td style='padding: 8px;'><b><a href='https://github.com/luizmoretti/Django_ERP/blob/master/BackEnd/apps/inventory/transfer/services/reports.py'>reports.py</a></b></td>
													<td style='padding: 8px;'>- Generate comprehensive inventory transfer reports to facilitate data-driven decision-making and operational oversight within the backend system<br>- The functionality consolidates transfer data, enabling stakeholders to analyze transfer activities, track inventory movement, and ensure accurate record-keeping across the entire inventory management architecture.</td>
												</tr>
												<tr style='border-bottom: 1px solid #eee;'>
													<td style='padding: 8px;'><b><a href='https://github.com/luizmoretti/Django_ERP/blob/master/BackEnd/apps/inventory/transfer/services/handlers.py'>handlers.py</a></b></td>
													<td style='padding: 8px;'>- Defines core transfer operations within the inventory management system, including creation, updating, approval, and rejection of transfer records<br>- Ensures transactional integrity and enforces business rules through validation, facilitating seamless and consistent handling of inventory transfers across warehouses<br>- Integrates with models and validators to maintain data accuracy and process compliance within the overall backend architecture.</td>
												</tr>
												<tr style='border-bottom: 1px solid #eee;'>
													<td style='padding: 8px;'><b><a href='https://github.com/luizmoretti/Django_ERP/blob/master/BackEnd/apps/inventory/transfer/services/validators.py'>validators.py</a></b></td>
													<td style='padding: 8px;'>- Defines validation rules for transfer operations within the inventory management system, ensuring compliance with business logic such as company access, transfer status, warehouse differentiation, item presence, and rejection reasons<br>- Supports maintaining data integrity and enforcing process constraints across transfer workflows, thereby facilitating reliable and consistent inventory transfers aligned with organizational policies.</td>
												</tr>
											</table>
										</blockquote>
									</details>
								</blockquote>
							</details>
							<!-- load_order Submodule -->
							<details>
								<summary><b>load_order</b></summary>
								<blockquote>
									<div class='directory-path' style='padding: 8px 0; color: #666;'>
										<code><b>⦿ BackEnd.apps.inventory.load_order</b></code>
									<table style='width: 100%; border-collapse: collapse;'>
									<thead>
										<tr style='background-color: #f8f9fa;'>
											<th style='width: 30%; text-align: left; padding: 8px;'>File Name</th>
											<th style='text-align: left; padding: 8px;'>Summary</th>
										</tr>
									</thead>
										<tr style='border-bottom: 1px solid #eee;'>
											<td style='padding: 8px;'><b><a href='https://github.com/luizmoretti/Django_ERP/blob/master/BackEnd/apps/inventory/load_order/tests.py'>tests.py</a></b></td>
											<td style='padding: 8px;'>- Provides test cases for the inventory load order functionality within the backend application, ensuring the correctness and reliability of inventory processing workflows<br>- Integrates with the overall architecture by validating data handling and business logic related to inventory load operations, supporting robust and error-free inventory management across the system.</td>
										</tr>
										<tr style='border-bottom: 1px solid #eee;'>
											<td style='padding: 8px;'><b><a href='https://github.com/luizmoretti/Django_ERP/blob/master/BackEnd/apps/inventory/load_order/views.py'>views.py</a></b></td>
											<td style='padding: 8px;'>- Provides RESTful API endpoints for managing inventory load orders, enabling users to list, create, retrieve, update, partially update, and delete load orders<br>- Ensures secure access through authentication, maintains data integrity with transactional operations, and integrates comprehensive API documentation for seamless integration within the overall inventory management architecture.</td>
										</tr>
										<tr style='border-bottom: 1px solid #eee;'>
											<td style='padding: 8px;'><b><a href='https://github.com/luizmoretti/Django_ERP/blob/master/BackEnd/apps/inventory/load_order/apps.py'>apps.py</a></b></td>
											<td style='padding: 8px;'>- Defines the configuration for the load order management component within the inventory system, establishing its integration point in the Django project architecture<br>- Facilitates the organization and initialization of load order functionalities, ensuring seamless inclusion of load order processes in the overall inventory management workflow<br>- Supports modularity and maintainability of the backend application.</td>
										</tr>
										<tr style='border-bottom: 1px solid #eee;'>
											<td style='padding: 8px;'><b><a href='https://github.com/luizmoretti/Django_ERP/blob/master/BackEnd/apps/inventory/load_order/admin.py'>admin.py</a></b></td>
											<td style='padding: 8px;'>- Defines the administrative interface for managing load orders and their associated items within the inventory system<br>- Facilitates efficient data entry, review, and filtering of load order records, ensuring streamlined oversight of order details and related items<br>- Integrates seamlessly into the overall backend architecture to support inventory tracking and order management workflows.</td>
										</tr>
										<tr style='border-bottom: 1px solid #eee;'>
											<td style='padding: 8px;'><b><a href='https://github.com/luizmoretti/Django_ERP/blob/master/BackEnd/apps/inventory/load_order/serializers.py'>serializers.py</a></b></td>
											<td style='padding: 8px;'>- Defines serializers for managing load order data, enabling creation, validation, and updates of load orders and their associated items within the inventory system<br>- Facilitates seamless data transformation between models and API responses, ensuring data integrity and consistency during load order processing and related transactions in the backend architecture.</td>
										</tr>
										<tr style='border-bottom: 1px solid #eee;'>
											<td style='padding: 8px;'><b><a href='https://github.com/luizmoretti/Django_ERP/blob/master/BackEnd/apps/inventory/load_order/models.py'>models.py</a></b></td>
											<td style='padding: 8px;'>- Defines the data models for managing load orders and their items within the inventory system<br>- Facilitates creation, tracking, and association of load orders with customers, vehicles, and products, ensuring unique order numbers and maintaining data integrity across related entities in the supply chain workflow.</td>
										</tr>
										<tr style='border-bottom: 1px solid #eee;'>
											<td style='padding: 8px;'><b><a href='https://github.com/luizmoretti/Django_ERP/blob/master/BackEnd/apps/inventory/load_order/urls.py'>urls.py</a></b></td>
											<td style='padding: 8px;'>- Defines URL routing for inventory load order management, enabling creation, retrieval, updating, and deletion of load orders<br>- Serves as the primary interface for interacting with load order data within the backend architecture, facilitating seamless API access and integration for inventory operations<br>- Ensures organized and consistent endpoint structure aligned with the overall system design.</td>
										</tr>
									</table>
									<!-- notifications Submodule -->
									<details>
										<summary><b>notifications</b></summary>
										<blockquote>
											<div class='directory-path' style='padding: 8px 0; color: #666;'>
												<code><b>⦿ BackEnd.apps.inventory.load_order.notifications</b></code>
											<table style='width: 100%; border-collapse: collapse;'>
											<thead>
												<tr style='background-color: #f8f9fa;'>
													<th style='width: 30%; text-align: left; padding: 8px;'>File Name</th>
													<th style='text-align: left; padding: 8px;'>Summary</th>
												</tr>
											</thead>
												<tr style='border-bottom: 1px solid #eee;'>
													<td style='padding: 8px;'><b><a href='https://github.com/luizmoretti/Django_ERP/blob/master/BackEnd/apps/inventory/load_order/notifications/constants.py'>constants.py</a></b></td>
													<td style='padding: 8px;'>- Defines constant values for notification-related components within the inventory load order module, facilitating consistent messaging and configuration across the backend system<br>- Supports streamlined management of notification parameters, ensuring reliable communication workflows integral to the inventory load order process within the overall application architecture.</td>
												</tr>
												<tr style='border-bottom: 1px solid #eee;'>
													<td style='padding: 8px;'><b><a href='https://github.com/luizmoretti/Django_ERP/blob/master/BackEnd/apps/inventory/load_order/notifications/serializers.py'>serializers.py</a></b></td>
													<td style='padding: 8px;'>- Defines serialization logic for inventory load order notifications, enabling consistent data formatting and transfer within the backend system<br>- Facilitates communication between components by converting notification data into structured formats suitable for processing, storage, or API responses, thereby supporting reliable and efficient handling of inventory load order events across the applications architecture.</td>
												</tr>
												<tr style='border-bottom: 1px solid #eee;'>
													<td style='padding: 8px;'><b><a href='https://github.com/luizmoretti/Django_ERP/blob/master/BackEnd/apps/inventory/load_order/notifications/handlers.py'>handlers.py</a></b></td>
													<td style='padding: 8px;'>- Facilitates the management and dispatch of notifications related to load order events within the inventory application<br>- Integrates with the broader backend architecture to ensure timely communication of load order status updates, supporting seamless operational workflows and enhancing real-time visibility across inventory processes.</td>
												</tr>
											</table>
										</blockquote>
									</details>
									<!-- services Submodule -->
									<details>
										<summary><b>services</b></summary>
										<blockquote>
											<div class='directory-path' style='padding: 8px 0; color: #666;'>
												<code><b>⦿ BackEnd.apps.inventory.load_order.services</b></code>
											<table style='width: 100%; border-collapse: collapse;'>
											<thead>
												<tr style='background-color: #f8f9fa;'>
													<th style='width: 30%; text-align: left; padding: 8px;'>File Name</th>
													<th style='text-align: left; padding: 8px;'>Summary</th>
												</tr>
											</thead>
												<tr style='border-bottom: 1px solid #eee;'>
													<td style='padding: 8px;'><b><a href='https://github.com/luizmoretti/Django_ERP/blob/master/BackEnd/apps/inventory/load_order/services/reports.py'>reports.py</a></b></td>
													<td style='padding: 8px;'>- Provides comprehensive load order reporting capabilities, including daily, weekly, and vehicle-specific summaries<br>- Facilitates insights into order volumes, item quantities, and distribution across vehicles and customers, supporting operational analysis and decision-making within the inventory management system<br>- Ensures accurate aggregation and logging for reliable performance tracking across the supply chain.</td>
												</tr>
												<tr style='border-bottom: 1px solid #eee;'>
													<td style='padding: 8px;'><b><a href='https://github.com/luizmoretti/Django_ERP/blob/master/BackEnd/apps/inventory/load_order/services/handlers.py'>handlers.py</a></b></td>
													<td style='padding: 8px;'>- Provides core operations for managing load orders within the inventory system, including creation, updating, and deletion of load orders and their associated items<br>- Ensures data validation, maintains transactional integrity, and logs key actions, facilitating seamless integration between order management, product, customer, and vehicle modules in the backend architecture.</td>
												</tr>
												<tr style='border-bottom: 1px solid #eee;'>
													<td style='padding: 8px;'><b><a href='https://github.com/luizmoretti/Django_ERP/blob/master/BackEnd/apps/inventory/load_order/services/validators.py'>validators.py</a></b></td>
													<td style='padding: 8px;'>- Provides validation logic for load order operations within the inventory management system, ensuring data integrity by verifying customer and vehicle existence, item details, stock availability, and vehicle capacity<br>- Facilitates reliable processing of load orders by enforcing business rules and preventing invalid or inconsistent data from entering the system.</td>
												</tr>
											</table>
										</blockquote>
									</details>
								</blockquote>
							</details>
							<!-- inflows Submodule -->
							<details>
								<summary><b>inflows</b></summary>
								<blockquote>
									<div class='directory-path' style='padding: 8px 0; color: #666;'>
										<code><b>⦿ BackEnd.apps.inventory.inflows</b></code>
									<table style='width: 100%; border-collapse: collapse;'>
									<thead>
										<tr style='background-color: #f8f9fa;'>
											<th style='width: 30%; text-align: left; padding: 8px;'>File Name</th>
											<th style='text-align: left; padding: 8px;'>Summary</th>
										</tr>
									</thead>
										<tr style='border-bottom: 1px solid #eee;'>
											<td style='padding: 8px;'><b><a href='https://github.com/luizmoretti/Django_ERP/blob/master/BackEnd/apps/inventory/inflows/tests.py'>tests.py</a></b></td>
											<td style='padding: 8px;'>- This test file is designed to validate the core functionalities related to inventory inflows within the backend system<br>- It ensures that inflow operations—such as adding stock to warehouses—adhere to business rules and data integrity constraints<br>- By setting up essential entities like companies, users, employees, products, warehouses, and suppliers, the tests simulate real-world scenarios to verify that inflow processes function correctly within the broader inventory management architecture<br>- Overall, this code helps maintain the reliability and correctness of inventory inflow handling, which is critical for accurate stock tracking and operational efficiency across the system.</td>
										</tr>
										<tr style='border-bottom: 1px solid #eee;'>
											<td style='padding: 8px;'><b><a href='https://github.com/luizmoretti/Django_ERP/blob/master/BackEnd/apps/inventory/inflows/permissions.py'>permissions.py</a></b></td>
											<td style='padding: 8px;'>- Defines permission classes to control user access to inventory inflow operations, ensuring actions like approval, rejection, and report generation are restricted based on user authentication, company association, and specific permissions<br>- Facilitates role-based access management within the inventory module, maintaining security and operational integrity across different user roles.</td>
										</tr>
										<tr style='border-bottom: 1px solid #eee;'>
											<td style='padding: 8px;'><b><a href='https://github.com/luizmoretti/Django_ERP/blob/master/BackEnd/apps/inventory/inflows/views.py'>views.py</a></b></td>
											<td style='padding: 8px;'>- This code defines the API views responsible for managing inventory inflow records within the backend architecture<br>- It facilitates core CRUD operations—listing, creating, retrieving, updating, and deleting inflow entries—while enforcing user authentication and permission checks<br>- By integrating with the Django REST Framework and schema documentation tools, it ensures secure, well-documented access to inflow data, supporting the broader inventory management systems functionality.</td>
										</tr>
										<tr style='border-bottom: 1px solid #eee;'>
											<td style='padding: 8px;'><b><a href='https://github.com/luizmoretti/Django_ERP/blob/master/BackEnd/apps/inventory/inflows/apps.py'>apps.py</a></b></td>
											<td style='padding: 8px;'>- Defines the configuration for the inventory inflows module within the Django project, establishing its application identity and ensuring the registration of relevant signals and notification handlers during startup<br>- Facilitates seamless integration of inflow-related processes, enabling automated responses and notifications to maintain accurate inventory tracking and operational workflows.</td>
										</tr>
										<tr style='border-bottom: 1px solid #eee;'>
											<td style='padding: 8px;'><b><a href='https://github.com/luizmoretti/Django_ERP/blob/master/BackEnd/apps/inventory/inflows/admin.py'>admin.py</a></b></td>
											<td style='padding: 8px;'>- Defines administrative interfaces for managing inventory inflows, enabling streamlined oversight of inflow records and associated items<br>- Facilitates efficient data entry, filtering, and searching within the backend, ensuring accurate tracking of inventory movements across origins and destinations<br>- Integrates related inflow items directly into inflow management, supporting comprehensive inventory oversight within the overall system architecture.</td>
										</tr>
										<tr style='border-bottom: 1px solid #eee;'>
											<td style='padding: 8px;'><b><a href='https://github.com/luizmoretti/Django_ERP/blob/master/BackEnd/apps/inventory/inflows/serializers.py'>serializers.py</a></b></td>
											<td style='padding: 8px;'>- Defines serializers for managing inventory inflows, enabling creation, retrieval, and updates of inflow records along with their associated items<br>- Facilitates validation, transactional integrity, and seamless integration of inflow data with related entities like products, suppliers, and warehouses, supporting efficient inventory tracking and management within the overall system architecture.</td>
										</tr>
										<tr style='border-bottom: 1px solid #eee;'>
											<td style='padding: 8px;'><b><a href='https://github.com/luizmoretti/Django_ERP/blob/master/BackEnd/apps/inventory/inflows/models.py'>models.py</a></b></td>
											<td style='padding: 8px;'>- Defines data models for managing inventory inflows, capturing details of incoming products and their sources<br>- Facilitates tracking of stock entries, associating products with specific inflows, suppliers, and warehouses<br>- Supports workflow states such as pending, approved, or rejected, enabling comprehensive oversight of inventory movements within the broader supply chain architecture.</td>
										</tr>
										<tr style='border-bottom: 1px solid #eee;'>
											<td style='padding: 8px;'><b><a href='https://github.com/luizmoretti/Django_ERP/blob/master/BackEnd/apps/inventory/inflows/signals.py'>signals.py</a></b></td>
											<td style='padding: 8px;'>- Implements signal handlers to manage inventory updates in response to inflow lifecycle events<br>- Ensures warehouse capacity validation, updates product and warehouse quantities upon inflow approval, creation, modification, or deletion, maintaining data consistency and integrity across inventory, warehouse, and product models within the overall system architecture.</td>
										</tr>
										<tr style='border-bottom: 1px solid #eee;'>
											<td style='padding: 8px;'><b><a href='https://github.com/luizmoretti/Django_ERP/blob/master/BackEnd/apps/inventory/inflows/urls.py'>urls.py</a></b></td>
											<td style='padding: 8px;'>- Defines URL routing for inventory inflow management, enabling CRUD operations and approval workflows<br>- Facilitates interaction with inflow records through standardized endpoints, supporting seamless integration within the broader inventory system architecture<br>- Ensures consistent access patterns for inflow data, streamlining inventory tracking and approval processes across the backend application.</td>
										</tr>
										<tr style='border-bottom: 1px solid #eee;'>
											<td style='padding: 8px;'><b><a href='https://github.com/luizmoretti/Django_ERP/blob/master/BackEnd/apps/inventory/inflows/tasks.py'>tasks.py</a></b></td>
											<td style='padding: 8px;'>- Generates a comprehensive daily inflow report summarizing inventory inflows over the past week, including total quantities, values, and supplier breakdowns<br>- Dispatches notifications to key stakeholders such as owners and executives with the report details, supporting data-driven decision-making within the inventory management architecture.</td>
										</tr>
									</table>
									<!-- notifications Submodule -->
									<details>
										<summary><b>notifications</b></summary>
										<blockquote>
											<div class='directory-path' style='padding: 8px 0; color: #666;'>
												<code><b>⦿ BackEnd.apps.inventory.inflows.notifications</b></code>
											<table style='width: 100%; border-collapse: collapse;'>
											<thead>
												<tr style='background-color: #f8f9fa;'>
													<th style='width: 30%; text-align: left; padding: 8px;'>File Name</th>
													<th style='text-align: left; padding: 8px;'>Summary</th>
												</tr>
											</thead>
												<tr style='border-bottom: 1px solid #eee;'>
													<td style='padding: 8px;'><b><a href='https://github.com/luizmoretti/Django_ERP/blob/master/BackEnd/apps/inventory/inflows/notifications/constants.py'>constants.py</a></b></td>
													<td style='padding: 8px;'>- Defines notification constants for the inventory inflows module, standardizing notification types, titles, messages, severities, priorities, and recipient roles<br>- Facilitates consistent and localized communication regarding inflow events, stock updates, and low stock alerts across the system, supporting effective user engagement and operational awareness within the overall inventory management architecture.</td>
												</tr>
												<tr style='border-bottom: 1px solid #eee;'>
													<td style='padding: 8px;'><b><a href='https://github.com/luizmoretti/Django_ERP/blob/master/BackEnd/apps/inventory/inflows/notifications/serializers.py'>serializers.py</a></b></td>
													<td style='padding: 8px;'>- Define serialization logic for inventory inflow notifications, enabling consistent data transformation and communication within the inventory management system<br>- Facilitates seamless data exchange between backend processes and external interfaces, ensuring accurate and structured notification delivery across the applications architecture<br>- This component supports reliable notification handling, contributing to the overall robustness of the inventory tracking and alerting mechanisms.</td>
												</tr>
												<tr style='border-bottom: 1px solid #eee;'>
													<td style='padding: 8px;'><b><a href='https://github.com/luizmoretti/Django_ERP/blob/master/BackEnd/apps/inventory/inflows/notifications/handlers.py'>handlers.py</a></b></td>
													<td style='padding: 8px;'>- Implements a notification handling system for inventory inflows, managing alerts for creation, updates, deletions, and stock level changes<br>- Ensures timely communication with relevant stakeholders by generating context-aware messages, facilitating transparency, accountability, and proactive stock management within the overall inventory architecture.</td>
												</tr>
											</table>
										</blockquote>
									</details>
									<!-- services Submodule -->
									<details>
										<summary><b>services</b></summary>
										<blockquote>
											<div class='directory-path' style='padding: 8px 0; color: #666;'>
												<code><b>⦿ BackEnd.apps.inventory.inflows.services</b></code>
											<table style='width: 100%; border-collapse: collapse;'>
											<thead>
												<tr style='background-color: #f8f9fa;'>
													<th style='width: 30%; text-align: left; padding: 8px;'>File Name</th>
													<th style='text-align: left; padding: 8px;'>Summary</th>
												</tr>
											</thead>
												<tr style='border-bottom: 1px solid #eee;'>
													<td style='padding: 8px;'><b><a href='https://github.com/luizmoretti/Django_ERP/blob/master/BackEnd/apps/inventory/inflows/services/reports.py'>reports.py</a></b></td>
													<td style='padding: 8px;'>- Provides comprehensive reporting capabilities for inventory inflows, enabling insights into daily activity, location-based trends, performance metrics, product dynamics, financial summaries, and audit trails<br>- Facilitates data-driven decision-making by aggregating and analyzing inflow data across various dimensions, supporting operational oversight, process optimization, and compliance within the overall inventory management architecture.</td>
												</tr>
												<tr style='border-bottom: 1px solid #eee;'>
													<td style='padding: 8px;'><b><a href='https://github.com/luizmoretti/Django_ERP/blob/master/BackEnd/apps/inventory/inflows/services/handlers.py'>handlers.py</a></b></td>
													<td style='padding: 8px;'>- Manages core business logic for inventory inflows, including creation, updates, approval, and rejection processes<br>- Ensures data validation, transactional integrity, and proper state transitions, facilitating seamless handling of inflow lifecycle events within the broader inventory management architecture<br>- Integrates validation and notification mechanisms to maintain consistency and traceability across the system.</td>
												</tr>
												<tr style='border-bottom: 1px solid #eee;'>
													<td style='padding: 8px;'><b><a href='https://github.com/luizmoretti/Django_ERP/blob/master/BackEnd/apps/inventory/inflows/services/validators.py'>validators.py</a></b></td>
													<td style='padding: 8px;'>- Provides core business validation logic for inventory inflow operations, ensuring resource access aligns with company policies, inflow statuses are appropriate for processing, and inflow items meet business rules<br>- It enforces data integrity and access control within the inventory management architecture, supporting reliable and compliant inflow handling across the system.</td>
												</tr>
											</table>
										</blockquote>
									</details>
								</blockquote>
							</details>
							<!-- outflows Submodule -->
							<details>
								<summary><b>outflows</b></summary>
								<blockquote>
									<div class='directory-path' style='padding: 8px 0; color: #666;'>
										<code><b>⦿ BackEnd.apps.inventory.outflows</b></code>
									<table style='width: 100%; border-collapse: collapse;'>
									<thead>
										<tr style='background-color: #f8f9fa;'>
											<th style='width: 30%; text-align: left; padding: 8px;'>File Name</th>
											<th style='text-align: left; padding: 8px;'>Summary</th>
										</tr>
									</thead>
										<tr style='border-bottom: 1px solid #eee;'>
											<td style='padding: 8px;'><b><a href='https://github.com/luizmoretti/Django_ERP/blob/master/BackEnd/apps/inventory/outflows/tests.py'>tests.py</a></b></td>
											<td style='padding: 8px;'>- Provides comprehensive tests for inventory outflow processes, ensuring stock validation, quantity updates, and transactional integrity within the warehouse management system<br>- Validates that stock levels are accurately maintained during outflow creation, updates, deletions, and error handling, thereby safeguarding inventory consistency and supporting reliable warehouse operations across the platform.</td>
										</tr>
										<tr style='border-bottom: 1px solid #eee;'>
											<td style='padding: 8px;'><b><a href='https://github.com/luizmoretti/Django_ERP/blob/master/BackEnd/apps/inventory/outflows/views.py'>views.py</a></b></td>
											<td style='padding: 8px;'>- Defines API endpoints for managing inventory outflows, including listing, creating, retrieving, updating, deleting, and processing approval or rejection actions<br>- Facilitates seamless handling of outflow lifecycle events, ensuring proper authorization, validation, and transaction management within the inventory system architecture<br>- Supports operational workflows for inventory dispatches and status updates.</td>
										</tr>
										<tr style='border-bottom: 1px solid #eee;'>
											<td style='padding: 8px;'><b><a href='https://github.com/luizmoretti/Django_ERP/blob/master/BackEnd/apps/inventory/outflows/apps.py'>apps.py</a></b></td>
											<td style='padding: 8px;'>- Defines the application configuration for inventory outflows within the backend architecture, establishing the modules identity and ensuring the registration of relevant signals during startup<br>- Facilitates integration of outflow-related processes into the overall inventory management system, supporting seamless event handling and modular organization of inventory operations.</td>
										</tr>
										<tr style='border-bottom: 1px solid #eee;'>
											<td style='padding: 8px;'><b><a href='https://github.com/luizmoretti/Django_ERP/blob/master/BackEnd/apps/inventory/outflows/admin.py'>admin.py</a></b></td>
											<td style='padding: 8px;'>- Defines administrative interfaces for managing inventory outflows, enabling streamlined oversight of outbound shipments within the backend system<br>- Facilitates viewing, filtering, and searching of outflow records, along with inline management of associated outflow items<br>- Enhances operational efficiency by providing clear, organized access to key outflow data, supporting inventory and logistics tracking across the platform.</td>
										</tr>
										<tr style='border-bottom: 1px solid #eee;'>
											<td style='padding: 8px;'><b><a href='https://github.com/luizmoretti/Django_ERP/blob/master/BackEnd/apps/inventory/outflows/serializers.py'>serializers.py</a></b></td>
											<td style='padding: 8px;'>- Defines serializers for managing inventory outflows, enabling creation, validation, and retrieval of outflow records and their associated items<br>- Facilitates seamless handling of warehouse-to-customer transfers by ensuring data integrity, product availability, and accurate tracking of related metadata within the overall inventory management architecture.</td>
										</tr>
										<tr style='border-bottom: 1px solid #eee;'>
											<td style='padding: 8px;'><b><a href='https://github.com/luizmoretti/Django_ERP/blob/master/BackEnd/apps/inventory/outflows/models.py'>models.py</a></b></td>
											<td style='padding: 8px;'>- Defines models for managing inventory outflows, capturing details of product removals from warehouses to customers<br>- Facilitates tracking of outflow origins, destinations, statuses, and associated items, supporting comprehensive inventory movement records within the broader supply chain architecture<br>- Enhances visibility into product dispatches and streamlines inventory management processes.</td>
										</tr>
										<tr style='border-bottom: 1px solid #eee;'>
											<td style='padding: 8px;'><b><a href='https://github.com/luizmoretti/Django_ERP/blob/master/BackEnd/apps/inventory/outflows/signals.py'>signals.py</a></b></td>
											<td style='padding: 8px;'>- Manages inventory outflow processes by ensuring accurate stock adjustments during creation, updates, approval, and deletion of outflow records<br>- Maintains data consistency across warehouse quantities, product stock levels, and outflow statuses, facilitating seamless inventory tracking and preventing stock discrepancies throughout the order fulfillment lifecycle.</td>
										</tr>
										<tr style='border-bottom: 1px solid #eee;'>
											<td style='padding: 8px;'><b><a href='https://github.com/luizmoretti/Django_ERP/blob/master/BackEnd/apps/inventory/outflows/urls.py'>urls.py</a></b></td>
											<td style='padding: 8px;'>- Defines URL routing for inventory outflow operations within the backend architecture, enabling clients to perform CRUD actions and approve or reject outflow requests<br>- Facilitates seamless interaction with outflow-related views, supporting inventory management workflows by providing structured endpoints for managing inventory outflow lifecycle events.</td>
										</tr>
									</table>
									<!-- notifications Submodule -->
									<details>
										<summary><b>notifications</b></summary>
										<blockquote>
											<div class='directory-path' style='padding: 8px 0; color: #666;'>
												<code><b>⦿ BackEnd.apps.inventory.outflows.notifications</b></code>
											<table style='width: 100%; border-collapse: collapse;'>
											<thead>
												<tr style='background-color: #f8f9fa;'>
													<th style='width: 30%; text-align: left; padding: 8px;'>File Name</th>
													<th style='text-align: left; padding: 8px;'>Summary</th>
												</tr>
											</thead>
												<tr style='border-bottom: 1px solid #eee;'>
													<td style='padding: 8px;'><b><a href='https://github.com/luizmoretti/Django_ERP/blob/master/BackEnd/apps/inventory/outflows/notifications/constants.py'>constants.py</a></b></td>
													<td style='padding: 8px;'>- Defines notification constants for the inventory outflows module, facilitating standardized messaging and alerting across the system<br>- It categorizes notification types, titles, messages, severity levels, and recipient groups, enabling consistent and localized communication for outflow events such as creation, approval, rejection, cancellation, and completion within the broader application architecture.</td>
												</tr>
												<tr style='border-bottom: 1px solid #eee;'>
													<td style='padding: 8px;'><b><a href='https://github.com/luizmoretti/Django_ERP/blob/master/BackEnd/apps/inventory/outflows/notifications/serializers.py'>serializers.py</a></b></td>
													<td style='padding: 8px;'>- Defines serialization logic for inventory outflow notifications, enabling consistent data transformation and communication within the notification system<br>- Facilitates seamless integration of notification data with external services or frontend components, supporting reliable and structured delivery of inventory movement alerts across the applications architecture.</td>
												</tr>
												<tr style='border-bottom: 1px solid #eee;'>
													<td style='padding: 8px;'><b><a href='https://github.com/luizmoretti/Django_ERP/blob/master/BackEnd/apps/inventory/outflows/notifications/handlers.py'>handlers.py</a></b></td>
													<td style='padding: 8px;'>- Facilitates automated notifications related to inventory outflows, including creation, approval, rejection, and delivery events<br>- Integrates with Django signals to trigger alerts, ensuring stakeholders are promptly informed of status changes and key actions within the inventory management process<br>- Enhances operational transparency and communication efficiency across the supply chain.</td>
												</tr>
											</table>
										</blockquote>
									</details>
									<!-- services Submodule -->
									<details>
										<summary><b>services</b></summary>
										<blockquote>
											<div class='directory-path' style='padding: 8px 0; color: #666;'>
												<code><b>⦿ BackEnd.apps.inventory.outflows.services</b></code>
											<table style='width: 100%; border-collapse: collapse;'>
											<thead>
												<tr style='background-color: #f8f9fa;'>
													<th style='width: 30%; text-align: left; padding: 8px;'>File Name</th>
													<th style='text-align: left; padding: 8px;'>Summary</th>
												</tr>
											</thead>
												<tr style='border-bottom: 1px solid #eee;'>
													<td style='padding: 8px;'><b><a href='https://github.com/luizmoretti/Django_ERP/blob/master/BackEnd/apps/inventory/outflows/services/reports.py'>reports.py</a></b></td>
													<td style='padding: 8px;'>- Generate comprehensive inventory outflow reports to facilitate data-driven decision-making and operational oversight within the backend system<br>- The functionality consolidates and analyzes inventory movement data, supporting accurate tracking and reporting of stock outflows across various categories, thereby enhancing inventory management efficiency and strategic planning within the overall architecture.</td>
												</tr>
												<tr style='border-bottom: 1px solid #eee;'>
													<td style='padding: 8px;'><b><a href='https://github.com/luizmoretti/Django_ERP/blob/master/BackEnd/apps/inventory/outflows/services/handlers.py'>handlers.py</a></b></td>
													<td style='padding: 8px;'>- Defines core business logic for managing inventory outflows, including creation, updating, approval, and rejection processes<br>- Ensures transactional integrity and enforces validation rules to maintain data consistency and compliance within the inventory management architecture<br>- Serves as a central service layer facilitating seamless outflow operations aligned with organizational workflows.</td>
												</tr>
												<tr style='border-bottom: 1px solid #eee;'>
													<td style='padding: 8px;'><b><a href='https://github.com/luizmoretti/Django_ERP/blob/master/BackEnd/apps/inventory/outflows/services/validators.py'>validators.py</a></b></td>
													<td style='padding: 8px;'>- Defines validation logic for inventory outflows, ensuring compliance with business rules<br>- It enforces company access permissions, verifies outflow status and items, and mandates descriptive rejection reasons<br>- Integral to maintaining data integrity and operational consistency within the inventory management architecture, it supports reliable processing of outflow transactions across the system.</td>
												</tr>
											</table>
										</blockquote>
									</details>
								</blockquote>
							</details>
						</blockquote>
					</details>
					<!-- delivery Submodule -->
					<details>
						<summary><b>delivery</b></summary>
						<blockquote>
							<div class='directory-path' style='padding: 8px 0; color: #666;'>
								<code><b>⦿ BackEnd.apps.delivery</b></code>
							<table style='width: 100%; border-collapse: collapse;'>
							<thead>
								<tr style='background-color: #f8f9fa;'>
									<th style='width: 30%; text-align: left; padding: 8px;'>File Name</th>
									<th style='text-align: left; padding: 8px;'>Summary</th>
								</tr>
							</thead>
								<tr style='border-bottom: 1px solid #eee;'>
									<td style='padding: 8px;'><b><a href='https://github.com/luizmoretti/Django_ERP/blob/master/BackEnd/apps/delivery/views.py'>views.py</a></b></td>
									<td style='padding: 8px;'>- The <code>views.py</code> file in the <code>BackEnd/apps/delivery</code> module serves as the central interface for managing delivery-related operations within the applications backend architecture<br>- It orchestrates the handling of delivery data, including creation, retrieval, updates, and deletion, while enforcing access controls and validation rules<br>- By integrating real-time communication channels and leveraging service layers, this code facilitates seamless delivery status updates, monitoring, and reporting<br>- Overall, it acts as the pivotal component that connects client requests to the underlying delivery management logic, ensuring a cohesive and responsive delivery workflow across the system.</td>
								</tr>
								<tr style='border-bottom: 1px solid #eee;'>
									<td style='padding: 8px;'><b><a href='https://github.com/luizmoretti/Django_ERP/blob/master/BackEnd/apps/delivery/apps.py'>apps.py</a></b></td>
									<td style='padding: 8px;'>- Defines the delivery application within the Django project, establishing its configuration and integration into the overall architecture<br>- It ensures the delivery module is correctly registered and recognized by the framework, facilitating the organization and management of delivery-related functionalities across the backend system<br>- This setup supports modular development and streamlined deployment of delivery features.</td>
								</tr>
								<tr style='border-bottom: 1px solid #eee;'>
									<td style='padding: 8px;'><b><a href='https://github.com/luizmoretti/Django_ERP/blob/master/BackEnd/apps/delivery/README.md'>README.md</a></b></td>
									<td style='padding: 8px;'>- Implements core delivery management and real-time tracking functionalities, enabling seamless coordination between delivery creation, location updates, and status transitions<br>- Integrates REST API and WebSocket communications to facilitate live monitoring for customers, drivers, and managers, while ensuring data integrity, validation, and secure access within a scalable architecture.</td>
								</tr>
								<tr style='border-bottom: 1px solid #eee;'>
									<td style='padding: 8px;'><b><a href='https://github.com/luizmoretti/Django_ERP/blob/master/BackEnd/apps/delivery/admin.py'>admin.py</a></b></td>
									<td style='padding: 8px;'>- Facilitates administrative management of delivery-related data within the Django backend<br>- It registers models for streamlined handling and customization in the Django admin interface, supporting efficient oversight and configuration of delivery operations<br>- This integration enhances overall system maintainability and user accessibility for backend administrators managing delivery workflows.</td>
								</tr>
								<tr style='border-bottom: 1px solid #eee;'>
									<td style='padding: 8px;'><b><a href='https://github.com/luizmoretti/Django_ERP/blob/master/BackEnd/apps/delivery/routing.py'>routing.py</a></b></td>
									<td style='padding: 8px;'>- Defines WebSocket routing for delivery updates, enabling real-time communication between the server and delivery clients<br>- It maps specific delivery identifiers to the corresponding consumer, facilitating live tracking and status updates within the overall backend architecture<br>- This setup ensures efficient, scalable delivery event handling integral to the applications real-time delivery management system.</td>
								</tr>
								<tr style='border-bottom: 1px solid #eee;'>
									<td style='padding: 8px;'><b><a href='https://github.com/luizmoretti/Django_ERP/blob/master/BackEnd/apps/delivery/consumer.py'>consumer.py</a></b></td>
									<td style='padding: 8px;'>- Facilitates real-time delivery tracking by managing WebSocket connections, handling location and status updates, and ensuring secure user access based on roles<br>- Enables seamless communication between delivery entities and clients, providing live updates on delivery progress while maintaining permission controls within the overall backend architecture.</td>
								</tr>
								<tr style='border-bottom: 1px solid #eee;'>
									<td style='padding: 8px;'><b><a href='https://github.com/luizmoretti/Django_ERP/blob/master/BackEnd/apps/delivery/serializers.py'>serializers.py</a></b></td>
									<td style='padding: 8px;'>- Defines serializers for managing delivery data, including creation, updates, and detailed representation of delivery statuses, checkpoints, and related entities such as customers, drivers, vehicles, and load orders<br>- Facilitates seamless data validation, serialization, and transactional integrity within the delivery management workflow, supporting comprehensive tracking and relationship handling across the backend architecture.</td>
								</tr>
								<tr style='border-bottom: 1px solid #eee;'>
									<td style='padding: 8px;'><b><a href='https://github.com/luizmoretti/Django_ERP/blob/master/BackEnd/apps/delivery/models.py'>models.py</a></b></td>
									<td style='padding: 8px;'>- Defines the data models for managing delivery operations, including tracking individual deliveries, their statuses, associated loads, vehicles, drivers, and customers<br>- Facilitates comprehensive delivery lifecycle management with real-time location updates, checkpoints, and status changes, integrating seamlessly into the broader logistics and supply chain architecture to ensure efficient and transparent delivery execution.</td>
								</tr>
								<tr style='border-bottom: 1px solid #eee;'>
									<td style='padding: 8px;'><b><a href='https://github.com/luizmoretti/Django_ERP/blob/master/BackEnd/apps/delivery/urls.py'>urls.py</a></b></td>
									<td style='padding: 8px;'>- Defines URL routing for delivery management, enabling CRUD operations, real-time location and status updates, checkpoint tracking, and report generation<br>- Integrates key endpoints to facilitate comprehensive delivery lifecycle handling within the backend architecture, supporting seamless interaction between client requests and delivery-related data processing.</td>
								</tr>
							</table>
							<!-- notifications Submodule -->
							<details>
								<summary><b>notifications</b></summary>
								<blockquote>
									<div class='directory-path' style='padding: 8px 0; color: #666;'>
										<code><b>⦿ BackEnd.apps.delivery.notifications</b></code>
									<table style='width: 100%; border-collapse: collapse;'>
									<thead>
										<tr style='background-color: #f8f9fa;'>
											<th style='width: 30%; text-align: left; padding: 8px;'>File Name</th>
											<th style='text-align: left; padding: 8px;'>Summary</th>
										</tr>
									</thead>
										<tr style='border-bottom: 1px solid #eee;'>
											<td style='padding: 8px;'><b><a href='https://github.com/luizmoretti/Django_ERP/blob/master/BackEnd/apps/delivery/notifications/constants.py'>constants.py</a></b></td>
											<td style='padding: 8px;'>- Define notification-related constants to standardize message types, statuses, and configurations across the backend delivery application<br>- These constants facilitate consistent handling of notifications, ensuring reliable communication workflows within the overall architecture, and support seamless integration with other modules responsible for user engagement and alert management.</td>
										</tr>
										<tr style='border-bottom: 1px solid #eee;'>
											<td style='padding: 8px;'><b><a href='https://github.com/luizmoretti/Django_ERP/blob/master/BackEnd/apps/delivery/notifications/handlers.py'>handlers.py</a></b></td>
											<td style='padding: 8px;'>- Facilitates the processing and management of notification events within the backend delivery system, ensuring timely and accurate delivery of notifications to users<br>- Integrates with other components to handle various notification types, supporting the overall architectures goal of reliable user communication and engagement<br>- Acts as a central point for notification handling logic, maintaining consistency across the platform.</td>
										</tr>
									</table>
								</blockquote>
							</details>
							<!-- services Submodule -->
							<details>
								<summary><b>services</b></summary>
								<blockquote>
									<div class='directory-path' style='padding: 8px 0; color: #666;'>
										<code><b>⦿ BackEnd.apps.delivery.services</b></code>
									<table style='width: 100%; border-collapse: collapse;'>
									<thead>
										<tr style='background-color: #f8f9fa;'>
											<th style='width: 30%; text-align: left; padding: 8px;'>File Name</th>
											<th style='text-align: left; padding: 8px;'>Summary</th>
										</tr>
									</thead>
										<tr style='border-bottom: 1px solid #eee;'>
											<td style='padding: 8px;'><b><a href='https://github.com/luizmoretti/Django_ERP/blob/master/BackEnd/apps/delivery/services/handlers.py'>handlers.py</a></b></td>
											<td style='padding: 8px;'>- Manages core delivery operations, including creation, updates, location tracking, and deletion, while ensuring data integrity through transactional handling<br>- Facilitates real-time communication via WebSocket notifications for status and location changes, supporting seamless coordination across delivery workflows within the broader logistics architecture.</td>
										</tr>
										<tr style='border-bottom: 1px solid #eee;'>
											<td style='padding: 8px;'><b><a href='https://github.com/luizmoretti/Django_ERP/blob/master/BackEnd/apps/delivery/services/validators.py'>validators.py</a></b></td>
											<td style='padding: 8px;'>- Provides comprehensive validation logic for delivery operations, ensuring data integrity and adherence to business rules<br>- Enforces correct status transitions, verifies associated entities like customers, drivers, vehicles, and load orders, and validates location updates<br>- Integral to maintaining consistent delivery workflows and preventing invalid or inconsistent data within the overall system architecture.</td>
										</tr>
									</table>
								</blockquote>
							</details>
							<!-- tasks Submodule -->
							<details>
								<summary><b>tasks</b></summary>
								<blockquote>
									<div class='directory-path' style='padding: 8px 0; color: #666;'>
										<code><b>⦿ BackEnd.apps.delivery.tasks</b></code>
									<table style='width: 100%; border-collapse: collapse;'>
									<thead>
										<tr style='background-color: #f8f9fa;'>
											<th style='width: 30%; text-align: left; padding: 8px;'>File Name</th>
											<th style='text-align: left; padding: 8px;'>Summary</th>
										</tr>
									</thead>
										<tr style='border-bottom: 1px solid #eee;'>
											<td style='padding: 8px;'><b><a href='https://github.com/luizmoretti/Django_ERP/blob/master/BackEnd/apps/delivery/tasks/handlers.py'>handlers.py</a></b></td>
											<td style='padding: 8px;'>- Handles asynchronous delivery-related operations such as notifying stakeholders of status changes, generating detailed delivery reports, cleaning outdated reports, and alerting managers about late deliveries<br>- These tasks support the overall delivery management system by ensuring timely communication, comprehensive record-keeping, and proactive issue resolution within the logistics architecture.</td>
										</tr>
									</table>
								</blockquote>
							</details>
						</blockquote>
					</details>
				</blockquote>
			</details>
			<!-- custom_settings Submodule -->
			<details>
				<summary><b>custom_settings</b></summary>
				<blockquote>
					<div class='directory-path' style='padding: 8px 0; color: #666;'>
						<code><b>⦿ BackEnd.custom_settings</b></code>
					<table style='width: 100%; border-collapse: collapse;'>
					<thead>
						<tr style='background-color: #f8f9fa;'>
							<th style='width: 30%; text-align: left; padding: 8px;'>File Name</th>
							<th style='text-align: left; padding: 8px;'>Summary</th>
						</tr>
					</thead>
						<tr style='border-bottom: 1px solid #eee;'>
							<td style='padding: 8px;'><b><a href='https://github.com/luizmoretti/Django_ERP/blob/master/BackEnd/custom_settings/apps.py'>apps.py</a></b></td>
							<td style='padding: 8px;'>- Defines the configuration for the custom_settings application within the Django project, establishing its identity and default auto-incrementing primary key type<br>- It integrates the custom_settings module into the overall project architecture, enabling proper registration and management of application-specific settings and functionalities.</td>
						</tr>
					</table>
					<!-- custom_middlewares Submodule -->
					<details>
						<summary><b>custom_middlewares</b></summary>
						<blockquote>
							<div class='directory-path' style='padding: 8px 0; color: #666;'>
								<code><b>⦿ BackEnd.custom_settings.custom_middlewares</b></code>
							<table style='width: 100%; border-collapse: collapse;'>
							<thead>
								<tr style='background-color: #f8f9fa;'>
									<th style='width: 30%; text-align: left; padding: 8px;'>File Name</th>
									<th style='text-align: left; padding: 8px;'>Summary</th>
								</tr>
							</thead>
								<tr style='border-bottom: 1px solid #eee;'>
									<td style='padding: 8px;'><b><a href='https://github.com/luizmoretti/Django_ERP/blob/master/BackEnd/custom_settings/custom_middlewares/apps.py'>apps.py</a></b></td>
									<td style='padding: 8px;'>- Defines the application configuration for custom middleware components within the backend architecture, enabling integration and initialization of middleware classes that handle JSON response formatting for 404 errors and anonymous user management<br>- Facilitates modular middleware setup, ensuring these custom functionalities are properly registered and activated within the Django project’s overall architecture.</td>
								</tr>
								<tr style='border-bottom: 1px solid #eee;'>
									<td style='padding: 8px;'><b><a href='https://github.com/luizmoretti/Django_ERP/blob/master/BackEnd/custom_settings/custom_middlewares/middleware.py'>middleware.py</a></b></td>
									<td style='padding: 8px;'>- Implements middleware to enhance API robustness by returning JSON-formatted 404 responses and handling exceptions uniformly<br>- Facilitates seamless schema generation for documentation tools by providing dummy user attributes during anonymous access<br>- Overall, it ensures consistent error handling and improves developer experience within the backend architecture.</td>
								</tr>
							</table>
						</blockquote>
					</details>
				</blockquote>
			</details>
			<!-- core Submodule -->
			<details>
				<summary><b>core</b></summary>
				<blockquote>
					<div class='directory-path' style='padding: 8px 0; color: #666;'>
						<code><b>⦿ BackEnd.core</b></code>
					<table style='width: 100%; border-collapse: collapse;'>
					<thead>
						<tr style='background-color: #f8f9fa;'>
							<th style='width: 30%; text-align: left; padding: 8px;'>File Name</th>
							<th style='text-align: left; padding: 8px;'>Summary</th>
						</tr>
					</thead>
						<tr style='border-bottom: 1px solid #eee;'>
							<td style='padding: 8px;'><b><a href='https://github.com/luizmoretti/Django_ERP/blob/master/BackEnd/core/unified_middleware.py'>unified_middleware.py</a></b></td>
							<td style='padding: 8px;'>- Implements a unified WebSocket authentication middleware that validates JWT tokens, associates users with WebSocket connections, and enforces delivery access permissions<br>- It supports both notification and delivery tracking channels, ensuring secure, context-aware user authentication within the applications real-time communication architecture.</td>
						</tr>
						<tr style='border-bottom: 1px solid #eee;'>
							<td style='padding: 8px;'><b><a href='https://github.com/luizmoretti/Django_ERP/blob/master/BackEnd/core/celery.py'>celery.py</a></b></td>
							<td style='padding: 8px;'>- Configures and manages background task execution within the backend architecture, enabling scheduled and asynchronous operations<br>- It orchestrates periodic tasks such as inflow report generation and stock checks, ensuring timely data processing and system maintenance<br>- This setup enhances operational efficiency and reliability by automating routine processes across the warehouse management system.</td>
						</tr>
						<tr style='border-bottom: 1px solid #eee;'>
							<td style='padding: 8px;'><b><a href='https://github.com/luizmoretti/Django_ERP/blob/master/BackEnd/core/update_dependencies.py'>update_dependencies.py</a></b></td>
							<td style='padding: 8px;'>- Automates dependency management by checking for outdated packages listed in requirements.txt, prompting for updates, and synchronizing the file with the latest versions<br>- Enhances project stability and security through streamlined verification and upgrade processes, ensuring the backend environment remains current and consistent with minimal manual intervention.</td>
						</tr>
						<tr style='border-bottom: 1px solid #eee;'>
							<td style='padding: 8px;'><b><a href='https://github.com/luizmoretti/Django_ERP/blob/master/BackEnd/core/wsgi.py'>wsgi.py</a></b></td>
							<td style='padding: 8px;'>- Provides the WSGI interface for deploying the Django application, enabling communication between the web server and the core backend<br>- It facilitates the handling of incoming HTTP requests and ensures proper application startup within the deployment environment, serving as a crucial entry point for production server integration within the overall project architecture.</td>
						</tr>
						<tr style='border-bottom: 1px solid #eee;'>
							<td style='padding: 8px;'><b><a href='https://github.com/luizmoretti/Django_ERP/blob/master/BackEnd/core/email_handlers.py'>email_handlers.py</a></b></td>
							<td style='padding: 8px;'>- Provides email handling capabilities within the backend architecture, enabling automated and templated communication for key workflows such as purchase order notifications and user authentication<br>- Facilitates reliable email delivery, template rendering, and context management, supporting seamless integration of email notifications into the overall system processes and user interactions.</td>
						</tr>
						<tr style='border-bottom: 1px solid #eee;'>
							<td style='padding: 8px;'><b><a href='https://github.com/luizmoretti/Django_ERP/blob/master/BackEnd/core/asgi.py'>asgi.py</a></b></td>
							<td style='padding: 8px;'>- Configures the ASGI application to handle both HTTP and WebSocket protocols within the project, integrating multiple WebSocket routes from different modules<br>- It establishes a unified, middleware-enhanced entry point for real-time communication features, ensuring secure and scalable WebSocket connections in development and production environments.</td>
						</tr>
						<tr style='border-bottom: 1px solid #eee;'>
							<td style='padding: 8px;'><b><a href='https://github.com/luizmoretti/Django_ERP/blob/master/BackEnd/core/urls.py'>urls.py</a></b></td>
							<td style='padding: 8px;'>- Defines URL routing for the backend, connecting API endpoints, admin interface, and authentication services to facilitate client-server communication<br>- Serves as the central configuration point for directing incoming requests to appropriate views, supporting both development and production environments within the overall application architecture.</td>
						</tr>
						<tr style='border-bottom: 1px solid #eee;'>
							<td style='padding: 8px;'><b><a href='https://github.com/luizmoretti/Django_ERP/blob/master/BackEnd/core/settings.py'>settings.py</a></b></td>
							<td style='padding: 8px;'>- This code file defines the core configuration settings for the Django-based backend of the project<br>- It establishes essential parameters such as security keys, debug mode, allowed hosts, and environment variable management, forming the foundation for the applications environment setup<br>- By centralizing these settings, it ensures consistent configuration across the codebase, facilitating secure deployment and environment-specific customization within the overall architecture.</td>
						</tr>
						<tr style='border-bottom: 1px solid #eee;'>
							<td style='padding: 8px;'><b><a href='https://github.com/luizmoretti/Django_ERP/blob/master/BackEnd/core/cache.py'>cache.py</a></b></td>
							<td style='padding: 8px;'>- Provides caching utilities to optimize data retrieval and response performance within the DryWall Warehouse ERP system<br>- Facilitates efficient storage, retrieval, and invalidation of cached data for various entities such as products, warehouses, and movements, thereby enhancing system responsiveness and reducing backend load across the architecture.</td>
						</tr>
					</table>
					<!-- constants Submodule -->
					<details>
						<summary><b>constants</b></summary>
						<blockquote>
							<div class='directory-path' style='padding: 8px 0; color: #666;'>
								<code><b>⦿ BackEnd.core.constants</b></code>
							<table style='width: 100%; border-collapse: collapse;'>
							<thead>
								<tr style='background-color: #f8f9fa;'>
									<th style='width: 30%; text-align: left; padding: 8px;'>File Name</th>
									<th style='text-align: left; padding: 8px;'>Summary</th>
								</tr>
							</thead>
								<tr style='border-bottom: 1px solid #eee;'>
									<td style='padding: 8px;'><b><a href='https://github.com/luizmoretti/Django_ERP/blob/master/BackEnd/core/constants/choices.py'>choices.py</a></b></td>
									<td style='padding: 8px;'>- Defines standardized, translatable choices for user roles, organizational profiles, payment intervals, business details, vehicle specifications, delivery statuses, and lead management within the application<br>- These constants facilitate consistent data entry, validation, and internationalization across the entire backend architecture, supporting role-based access control, operational workflows, and business process management.</td>
								</tr>
							</table>
						</blockquote>
					</details>
				</blockquote>
			</details>
			<!-- api Submodule -->
			<details>
				<summary><b>api</b></summary>
				<blockquote>
					<div class='directory-path' style='padding: 8px 0; color: #666;'>
						<code><b>⦿ BackEnd.api</b></code>
					<table style='width: 100%; border-collapse: collapse;'>
					<thead>
						<tr style='background-color: #f8f9fa;'>
							<th style='width: 30%; text-align: left; padding: 8px;'>File Name</th>
							<th style='text-align: left; padding: 8px;'>Summary</th>
						</tr>
					</thead>
						<tr style='border-bottom: 1px solid #eee;'>
							<td style='padding: 8px;'><b><a href='https://github.com/luizmoretti/Django_ERP/blob/master/BackEnd/api/tests.py'>tests.py</a></b></td>
							<td style='padding: 8px;'>- Provides a foundation for testing backend API endpoints within the Django application, ensuring functionality and reliability<br>- It supports maintaining code quality by enabling the creation and execution of automated tests for API interactions, which is essential for validating the correctness of backend logic and facilitating ongoing development within the overall project architecture.</td>
						</tr>
						<tr style='border-bottom: 1px solid #eee;'>
							<td style='padding: 8px;'><b><a href='https://github.com/luizmoretti/Django_ERP/blob/master/BackEnd/api/views.py'>views.py</a></b></td>
							<td style='padding: 8px;'>- Provides JWT authentication endpoints for token issuance, refresh, and verification within the backend API<br>- Integrates with Django REST Framework and drf_spectacular to facilitate secure user authentication workflows, ensuring streamlined token management and validation as part of the overall application security architecture.</td>
						</tr>
						<tr style='border-bottom: 1px solid #eee;'>
							<td style='padding: 8px;'><b><a href='https://github.com/luizmoretti/Django_ERP/blob/master/BackEnd/api/apps.py'>apps.py</a></b></td>
							<td style='padding: 8px;'>- Defines the application configuration for the API module within the Django project, establishing its identity and default database auto-incrementing behavior<br>- It integrates the API component into the overall project architecture, enabling proper registration and management of API-related functionalities within the backend system<br>- This setup ensures the API app is correctly recognized and configured during project initialization.</td>
						</tr>
						<tr style='border-bottom: 1px solid #eee;'>
							<td style='padding: 8px;'><b><a href='https://github.com/luizmoretti/Django_ERP/blob/master/BackEnd/api/admin.py'>admin.py</a></b></td>
							<td style='padding: 8px;'>- Facilitates administrative management of backend data models within the Django framework<br>- It registers models for seamless integration into the Django admin interface, enabling authorized users to efficiently perform CRUD operations and oversee application data<br>- This file plays a crucial role in supporting backend data oversight, ensuring smooth administrative workflows within the overall project architecture.</td>
						</tr>
						<tr style='border-bottom: 1px solid #eee;'>
							<td style='padding: 8px;'><b><a href='https://github.com/luizmoretti/Django_ERP/blob/master/BackEnd/api/models.py'>models.py</a></b></td>
							<td style='padding: 8px;'>- Defines the data schema for core entities within the backend API, facilitating structured storage and retrieval of application data<br>- Serves as the foundation for data interactions across the system, enabling consistent management of models that underpin business logic and support seamless integration with other components of the Django-based architecture.</td>
						</tr>
						<tr style='border-bottom: 1px solid #eee;'>
							<td style='padding: 8px;'><b><a href='https://github.com/luizmoretti/Django_ERP/blob/master/BackEnd/api/urls.py'>urls.py</a></b></td>
							<td style='padding: 8px;'>- Defines the URL routing architecture for the backend API, orchestrating access to authentication, user management, notifications, company operations, inventory, delivery, vehicle, scheduling, and other core services<br>- It centralizes endpoint mappings, enabling seamless integration and navigation across diverse modules within the overall system, facilitating organized and scalable API interactions.</td>
						</tr>
					</table>
				</blockquote>
			</details>
			<!-- basemodels Submodule -->
			<details>
				<summary><b>basemodels</b></summary>
				<blockquote>
					<div class='directory-path' style='padding: 8px 0; color: #666;'>
						<code><b>⦿ BackEnd.basemodels</b></code>
					<table style='width: 100%; border-collapse: collapse;'>
					<thead>
						<tr style='background-color: #f8f9fa;'>
							<th style='width: 30%; text-align: left; padding: 8px;'>File Name</th>
							<th style='text-align: left; padding: 8px;'>Summary</th>
						</tr>
					</thead>
						<tr style='border-bottom: 1px solid #eee;'>
							<td style='padding: 8px;'><b><a href='https://github.com/luizmoretti/Django_ERP/blob/master/BackEnd/basemodels/tests.py'>tests.py</a></b></td>
							<td style='padding: 8px;'>- Provides foundational test cases for backend models, ensuring data integrity and consistency within the Django application<br>- Supports validation of model behaviors and interactions, contributing to the overall robustness and reliability of the codebase<br>- Serves as a critical component for maintaining quality standards across the backend architecture.</td>
						</tr>
						<tr style='border-bottom: 1px solid #eee;'>
							<td style='padding: 8px;'><b><a href='https://github.com/luizmoretti/Django_ERP/blob/master/BackEnd/basemodels/views.py'>views.py</a></b></td>
							<td style='padding: 8px;'>- Defines the view layer for backend models, facilitating the rendering of templates and user interface interactions within the Django application<br>- Serves as the entry point for handling HTTP requests related to core data models, supporting the overall architecture by enabling dynamic content delivery and user engagement in the web platform.</td>
						</tr>
						<tr style='border-bottom: 1px solid #eee;'>
							<td style='padding: 8px;'><b><a href='https://github.com/luizmoretti/Django_ERP/blob/master/BackEnd/basemodels/apps.py'>apps.py</a></b></td>
							<td style='padding: 8px;'>- Defines the configuration for the basemodels application within the Django project, establishing its identity and default settings<br>- It integrates the core models and functionalities into the overall architecture, enabling consistent database interactions and facilitating the extension of foundational data structures across the backend system.</td>
						</tr>
						<tr style='border-bottom: 1px solid #eee;'>
							<td style='padding: 8px;'><b><a href='https://github.com/luizmoretti/Django_ERP/blob/master/BackEnd/basemodels/admin.py'>admin.py</a></b></td>
							<td style='padding: 8px;'>- Facilitates administrative management of backend models within the Django framework by registering models for the admin interface<br>- Enhances the overall architecture by enabling streamlined data oversight and manipulation through the Django admin panel, supporting efficient backend operations and data integrity across the application.</td>
						</tr>
						<tr style='border-bottom: 1px solid #eee;'>
							<td style='padding: 8px;'><b><a href='https://github.com/luizmoretti/Django_ERP/blob/master/BackEnd/basemodels/models.py'>models.py</a></b></td>
							<td style='padding: 8px;'>- Defines foundational abstract models for the backend architecture, enabling consistent tracking of entity creation, updates, and associations with companies and users<br>- Facilitates automatic attribution of actions to authenticated users and standardizes address-related fields across various models, ensuring data integrity and streamlined auditability within the system.</td>
						</tr>
					</table>
				</blockquote>
			</details>
			<!-- DRF Docs Submodule -->
			<details>
				<summary><b>DRF Docs</b></summary>
				<blockquote>
					<div class='directory-path' style='padding: 8px 0; color: #666;'>
						<code><b>⦿ BackEnd.DRF Docs</b></code>
					<table style='width: 100%; border-collapse: collapse;'>
					<thead>
						<tr style='background-color: #f8f9fa;'>
							<th style='width: 30%; text-align: left; padding: 8px;'>File Name</th>
							<th style='text-align: left; padding: 8px;'>Summary</th>
						</tr>
					</thead>
						<tr style='border-bottom: 1px solid #eee;'>
							<td style='padding: 8px;'><b><a href='https://github.com/luizmoretti/Django_ERP/blob/master/BackEnd/DRF Docs/Django Rest Framework Documentation - Generic Views.md'>Django Rest Framework Documentation - Generic Views.md</a></b></td>
							<td style='padding: 8px;'>- The code file <code>Django Rest Framework Documentation-Generic Views.md</code> serves as a comprehensive overview of the DRFs generic views, which are designed to streamline the development of RESTful APIs<br>- It highlights how these views abstract common patterns in view creation, enabling rapid, reusable, and maintainable API development that closely aligns with database models<br>- Within the overall architecture, this documentation underscores the foundational role of generic views in facilitating efficient, standardized, and scalable API endpoints across the backend system.</td>
						</tr>
						<tr style='border-bottom: 1px solid #eee;'>
							<td style='padding: 8px;'><b><a href='https://github.com/luizmoretti/Django_ERP/blob/master/BackEnd/DRF Docs/Django Rest Framework Documentation - Throttling.md'>Django Rest Framework Documentation - Throttling.md</a></b></td>
							<td style='padding: 8px;'>- Defines the API throttling mechanisms within the Django REST framework, enabling rate limiting to control client request flow<br>- It supports multiple throttling strategies, including per-user, per-IP, and scoped limits, facilitating flexible management of resource usage and protecting against overuse while allowing customization for different API segments.</td>
						</tr>
						<tr style='border-bottom: 1px solid #eee;'>
							<td style='padding: 8px;'><b><a href='https://github.com/luizmoretti/Django_ERP/blob/master/BackEnd/DRF Docs/Django Rest Framework Documentation - Format Suffixes.md'>Django Rest Framework Documentation - Format Suffixes.md</a></b></td>
							<td style='padding: 8px;'>- Provides guidance on implementing URL format suffixes in Django REST Framework APIs to enable clients to specify response formats via URL extensions<br>- Facilitates flexible content negotiation, supporting multiple media types such as JSON and HTML, and integrates seamlessly with internationalization patterns<br>- Enhances API usability by allowing clients to request specific data representations efficiently within the overall backend architecture.</td>
						</tr>
						<tr style='border-bottom: 1px solid #eee;'>
							<td style='padding: 8px;'><b><a href='https://github.com/luizmoretti/Django_ERP/blob/master/BackEnd/DRF Docs/Django Rest Framework Documentation - Versioning.md'>Django Rest Framework Documentation - Versioning.md</a></b></td>
							<td style='padding: 8px;'>- Defines the API versioning strategy within the Django REST Framework architecture, enabling clients to access different API versions through various schemes such as URL path, headers, hostname, or query parameters<br>- Facilitates seamless evolution of the API by allowing behavior and serialization changes based on client-specified version information, ensuring backward compatibility and controlled feature rollout across the entire system.</td>
						</tr>
						<tr style='border-bottom: 1px solid #eee;'>
							<td style='padding: 8px;'><b><a href='https://github.com/luizmoretti/Django_ERP/blob/master/BackEnd/DRF Docs/Django Rest Framework Documentation - Parsers.md'>Django Rest Framework Documentation - Parsers.md</a></b></td>
							<td style='padding: 8px;'>- Defines and manages various request content parsers within the Django REST Framework architecture, enabling the API to interpret and process multiple media types such as JSON, form data, multipart uploads, and custom formats<br>- Facilitates flexible data ingestion by selecting appropriate parsers based on request headers, supporting both built-in and custom parsing strategies to ensure seamless data handling across diverse client interactions.</td>
						</tr>
						<tr style='border-bottom: 1px solid #eee;'>
							<td style='padding: 8px;'><b><a href='https://github.com/luizmoretti/Django_ERP/blob/master/BackEnd/DRF Docs/Django Rest Framework Documentation - Returning URLs.md'>Django Rest Framework Documentation - Returning URLs.md</a></b></td>
							<td style='padding: 8px;'>- Facilitates the generation of absolute URLs within the Django REST Framework, enhancing API discoverability and navigation<br>- By providing utility functions that produce fully qualified links based on request context, it supports REST principles of hypermedia-driven APIs, ensuring clients can reliably resolve resource locations and improve overall API usability across the architecture.</td>
						</tr>
						<tr style='border-bottom: 1px solid #eee;'>
							<td style='padding: 8px;'><b><a href='https://github.com/luizmoretti/Django_ERP/blob/master/BackEnd/DRF Docs/Django Rest Framework Documentation - Pagination.md'>Django Rest Framework Documentation - Pagination.md</a></b></td>
							<td style='padding: 8px;'>- This code file provides documentation and implementation support for pagination within the Django REST Framework (DRF)<br>- Its primary purpose is to facilitate efficient data retrieval by dividing large datasets into manageable pages, enhancing API performance and usability<br>- The pagination system supports customizable styles, allowing responses to include navigation links either within the response content or headers, with current emphasis on in-content links for better accessibility in the browsable API<br>- Overall, this component is integral to the backend architecture, ensuring scalable and user-friendly data access across the entire application.</td>
						</tr>
						<tr style='border-bottom: 1px solid #eee;'>
							<td style='padding: 8px;'><b><a href='https://github.com/luizmoretti/Django_ERP/blob/master/BackEnd/DRF Docs/Django Rest Framework Documentation - Viewsets.md'>Django Rest Framework Documentation - Viewsets.md</a></b></td>
							<td style='padding: 8px;'>- Defines a comprehensive framework for creating, managing, and customizing API endpoints through reusable ViewSet classes<br>- Facilitates streamlined routing, action handling, and permission management, enabling rapid development of consistent, scalable RESTful interfaces within the Django REST Framework architecture<br>- Supports both standard and custom behaviors, promoting code reuse and simplifying URL configuration across the API.</td>
						</tr>
						<tr style='border-bottom: 1px solid #eee;'>
							<td style='padding: 8px;'><b><a href='https://github.com/luizmoretti/Django_ERP/blob/master/BackEnd/DRF Docs/Django Rest Framework Documentation - Permissions.md'>Django Rest Framework Documentation - Permissions.md</a></b></td>
							<td style='padding: 8px;'>- The <code>permissions.py</code> file in this codebase defines the core logic for managing access control within the Django REST Framework (DRF)<br>- It establishes how the system determines whether a user or request has the necessary authorization to access specific API endpoints<br>- By implementing various permission classes, this file enables fine-grained control over user permissions, ensuring that only authorized entities can perform certain actions or view particular data<br>- Overall, it plays a crucial role in enforcing security and access policies across the applications API architecture.</td>
						</tr>
						<tr style='border-bottom: 1px solid #eee;'>
							<td style='padding: 8px;'><b><a href='https://github.com/luizmoretti/Django_ERP/blob/master/BackEnd/DRF Docs/Django Rest Framework Documentation - Validators.md'>Django Rest Framework Documentation - Validators.md</a></b></td>
							<td style='padding: 8px;'>- Provides reusable validation components for Django REST Framework serializers, enabling consistent enforcement of data integrity constraints such as uniqueness, date-based constraints, and custom rules<br>- Facilitates explicit validation logic, improves code clarity, and supports complex validation scenarios across the entire codebase architecture<br>- Enhances maintainability by centralizing validation logic and promoting best practices in API data validation.</td>
						</tr>
						<tr style='border-bottom: 1px solid #eee;'>
							<td style='padding: 8px;'><b><a href='https://github.com/luizmoretti/Django_ERP/blob/master/BackEnd/DRF Docs/Django Rest Framework Documentation - Requests.md'>Django Rest Framework Documentation - Requests.md</a></b></td>
							<td style='padding: 8px;'>- Provides an abstraction layer over Djangos standard HttpRequest to facilitate flexible request parsing, authentication, and content negotiation within the Django REST Framework<br>- Enables handling of diverse media types such as JSON and form data across various HTTP methods, supporting seamless API interactions, user authentication, and media type negotiation, thereby ensuring consistent and secure request processing across the entire architecture.</td>
						</tr>
						<tr style='border-bottom: 1px solid #eee;'>
							<td style='padding: 8px;'><b><a href='https://github.com/luizmoretti/Django_ERP/blob/master/BackEnd/DRF Docs/Django Rest Framework Documentation - Serializers Fields.md'>Django Rest Framework Documentation - Serializers Fields.md</a></b></td>
							<td style='padding: 8px;'>- This code file serves as a comprehensive reference for serializer fields within the Django REST Framework (DRF)<br>- It highlights how serializer fields facilitate the conversion, validation, and normalization of data between primitive types and internal representations, ensuring data integrity and consistency across the API layer<br>- Positioned within the broader backend architecture, these serializer fields underpin the data serialization and validation processes, enabling seamless data exchange between client requests and server-side models<br>- Overall, this file provides essential documentation that guides developers in effectively utilizing DRF serializer fields to maintain robust and reliable API endpoints.</td>
						</tr>
						<tr style='border-bottom: 1px solid #eee;'>
							<td style='padding: 8px;'><b><a href='https://github.com/luizmoretti/Django_ERP/blob/master/BackEnd/DRF Docs/Django Rest Framework Documentation - Caching.md'>Django Rest Framework Documentation - Caching.md</a></b></td>
							<td style='padding: 8px;'>- Provides guidance on implementing caching strategies within the Django REST Framework architecture to optimize API response performance<br>- It details how to leverage Djangos cache utilities with class-based views, viewsets, and function-based views, ensuring efficient data retrieval and reduced server load for user-specific and general endpoints<br>- This documentation supports scalable, high-performance API development.</td>
						</tr>
						<tr style='border-bottom: 1px solid #eee;'>
							<td style='padding: 8px;'><b><a href='https://github.com/luizmoretti/Django_ERP/blob/master/BackEnd/DRF Docs/Django Rest Framework Documentation - Serializers.md'>Django Rest Framework Documentation - Serializers.md</a></b></td>
							<td style='padding: 8px;'>- This code file serves as the core component for data serialization within the backend architecture, enabling the transformation of complex data structures such as querysets and model instances into standardized formats like JSON or XML<br>- It facilitates seamless data exchange between the server and clients by handling both serialization (converting data for responses) and deserialization (parsing incoming data), ensuring data integrity and validation<br>- Overall, it underpins the APIs ability to communicate structured data efficiently and reliably across the entire system.</td>
						</tr>
						<tr style='border-bottom: 1px solid #eee;'>
							<td style='padding: 8px;'><b><a href='https://github.com/luizmoretti/Django_ERP/blob/master/BackEnd/DRF Docs/Django Rest Framework Documentation - Status Codes.md'>Django Rest Framework Documentation - Status Codes.md</a></b></td>
							<td style='padding: 8px;'>- Provides a comprehensive reference for HTTP status codes used within the Django REST Framework, facilitating clear and consistent API responses<br>- It categorizes status codes by response type, offers helper functions for status evaluation, and aligns with RFC standards, supporting robust error handling and communication across the entire backend architecture.</td>
						</tr>
						<tr style='border-bottom: 1px solid #eee;'>
							<td style='padding: 8px;'><b><a href='https://github.com/luizmoretti/Django_ERP/blob/master/BackEnd/DRF Docs/Django Rest Framework Documentation - Routers.md'>Django Rest Framework Documentation - Routers.md</a></b></td>
							<td style='padding: 8px;'>- This code file serves as the core implementation of automatic URL routing within the Django REST Framework (DRF)<br>- It enables the entire backend architecture to efficiently map resource-based viewsets to standardized API endpoints, streamlining the process of defining and managing URL patterns<br>- By abstracting the routing logic, it promotes a consistent and scalable approach to connecting client requests with the appropriate backend logic across the project<br>- This facilitates rapid development, reduces boilerplate, and ensures that the API adheres to RESTful principles throughout the codebase.</td>
						</tr>
						<tr style='border-bottom: 1px solid #eee;'>
							<td style='padding: 8px;'><b><a href='https://github.com/luizmoretti/Django_ERP/blob/master/BackEnd/DRF Docs/Django Rest Framework Documentation - Metadata.md'>Django Rest Framework Documentation - Metadata.md</a></b></td>
							<td style='padding: 8px;'>- Defines the metadata handling mechanism for the Django REST Framework API, enabling clients to discover resource capabilities, supported methods, and schema details via OPTIONS requests<br>- Supports customization of metadata responses, facilitating schema generation and enhanced API introspection, which improves client integration and documentation consistency across the codebase.</td>
						</tr>
						<tr style='border-bottom: 1px solid #eee;'>
							<td style='padding: 8px;'><b><a href='https://github.com/luizmoretti/Django_ERP/blob/master/BackEnd/DRF Docs/Django Rest Framework Documentation - Responses.md'>Django Rest Framework Documentation - Responses.md</a></b></td>
							<td style='padding: 8px;'>- Defines the response handling mechanism within the Django REST Framework, enabling content negotiation and serialization of data into various formats for API responses<br>- Facilitates consistent, flexible, and content-aware communication between the server and clients, supporting multiple media types and simplifying response creation in web API architecture.</td>
						</tr>
						<tr style='border-bottom: 1px solid #eee;'>
							<td style='padding: 8px;'><b><a href='https://github.com/luizmoretti/Django_ERP/blob/master/BackEnd/DRF Docs/Django Rest Framework Documentation - Renderers.md'>Django Rest Framework Documentation - Renderers.md</a></b></td>
							<td style='padding: 8px;'>- This code file defines the rendering mechanisms within the Django REST Framework, serving as the core component responsible for converting server responses into various media formats before delivery to clients<br>- It facilitates flexible content negotiation by supporting multiple built-in renderers and enabling custom renderer creation, thereby ensuring that API responses are appropriately formatted according to client needs<br>- Overall, it plays a pivotal role in the response generation pipeline, bridging the servers data representations with the final byte streams transmitted over the network.</td>
						</tr>
						<tr style='border-bottom: 1px solid #eee;'>
							<td style='padding: 8px;'><b><a href='https://github.com/luizmoretti/Django_ERP/blob/master/BackEnd/DRF Docs/Django Rest Framework Documentation - Views.md'>Django Rest Framework Documentation - Views.md</a></b></td>
							<td style='padding: 8px;'>- Defines the core architecture for building RESTful API endpoints using class-based and function-based views within Django REST Framework<br>- Facilitates request handling, content negotiation, authentication, permissions, and exception management, ensuring consistent API behavior and extensibility across the codebase<br>- Serves as the foundation for implementing secure, flexible, and standardized API interactions.</td>
						</tr>
						<tr style='border-bottom: 1px solid #eee;'>
							<td style='padding: 8px;'><b><a href='https://github.com/luizmoretti/Django_ERP/blob/master/BackEnd/DRF Docs/Django Rest Framework Documentation - Testing.md'>Django Rest Framework Documentation - Testing.md</a></b></td>
							<td style='padding: 8px;'>- The code in <code>test.py</code> provides specialized testing utilities for the Django REST Framework, extending Djangos core testing framework to facilitate the creation and execution of API request tests<br>- It primarily introduces helper classes like <code>APIRequestFactory</code>, which streamline the process of simulating API interactions, ensuring the robustness and reliability of the API endpoints within the overall backend architecture<br>- This setup enables comprehensive, efficient testing of the REST API, contributing to the maintainability and correctness of the entire codebase.</td>
						</tr>
						<tr style='border-bottom: 1px solid #eee;'>
							<td style='padding: 8px;'><b><a href='https://github.com/luizmoretti/Django_ERP/blob/master/BackEnd/DRF Docs/Django Rest Framework Documentation - Content Negotiation.md'>Django Rest Framework Documentation - Content Negotiation.md</a></b></td>
							<td style='padding: 8px;'>- Defines the content negotiation mechanism within the Django REST Framework, enabling selection of appropriate response formats based on client preferences and server configurations<br>- It manages how the API determines the media type for responses, supporting default, custom, and view-specific negotiation strategies to ensure flexible and consistent content delivery across the application.</td>
						</tr>
						<tr style='border-bottom: 1px solid #eee;'>
							<td style='padding: 8px;'><b><a href='https://github.com/luizmoretti/Django_ERP/blob/master/BackEnd/DRF Docs/Django Rest Framework Documentation - Exceptions.md'>Django Rest Framework Documentation - Exceptions.md</a></b></td>
							<td style='padding: 8px;'>- Defines centralized exception handling for the Django REST Framework, enabling consistent and meaningful error responses across the API<br>- It categorizes various error types, such as validation, authentication, and permission issues, facilitating clear communication of issues to clients<br>- This setup ensures robust error management aligned with the overall architecture, enhancing API reliability and developer experience.</td>
						</tr>
						<tr style='border-bottom: 1px solid #eee;'>
							<td style='padding: 8px;'><b><a href='https://github.com/luizmoretti/Django_ERP/blob/master/BackEnd/DRF Docs/Django Rest Framework Documentation - Schemas.md'>Django Rest Framework Documentation - Schemas.md</a></b></td>
							<td style='padding: 8px;'>- This code file serves as a comprehensive reference for understanding how the Django REST Framework (DRF) generates and utilizes schemas within the backend architecture<br>- It highlights the role of schemas in describing available API resources, including their URLs, data representations, and supported operations, thereby facilitating API discoverability, documentation, and client integration<br>- While noting the deprecation of DRFs built-in schema generation in favor of third-party solutions, this documentation underscores the importance of schemas in maintaining a clear, machine-readable contract for the API, ensuring consistency and ease of use across the entire backend system.</td>
						</tr>
						<tr style='border-bottom: 1px solid #eee;'>
							<td style='padding: 8px;'><b><a href='https://github.com/luizmoretti/Django_ERP/blob/master/BackEnd/DRF Docs/Django Rest Framework Documentation - Serializers Relations.md'>Django Rest Framework Documentation - Serializers Relations.md</a></b></td>
							<td style='padding: 8px;'>- The <code>relations.py</code> file within the Django REST Framework (DRF) documentation serves as a foundational reference for implementing model relationships in API serialization<br>- It defines the data structures used to represent various relational fields—such as foreign keys, many-to-many, one-to-one, and generic relationships—ensuring that model associations are accurately and efficiently exposed through RESTful endpoints<br>- This component is integral to the overall architecture by enabling serializers to handle complex data relationships, facilitating seamless data serialization and deserialization across interconnected models within the backend system.</td>
						</tr>
						<tr style='border-bottom: 1px solid #eee;'>
							<td style='padding: 8px;'><b><a href='https://github.com/luizmoretti/Django_ERP/blob/master/BackEnd/DRF Docs/Django Rest Framework Documentation - Authentication.md'>Django Rest Framework Documentation - Authentication.md</a></b></td>
							<td style='padding: 8px;'>- The <code>authentication.py</code> file serves as a core component within the backend architecture, responsible for establishing the mechanism by which incoming API requests are associated with user credentials or tokens<br>- Its primary purpose is to facilitate pluggable authentication schemes, enabling the system to verify and identify users securely before any permission or throttling policies are enforced<br>- This setup ensures that each request is accurately linked to an authenticated identity, forming the foundation for secure and controlled access across the entire application.</td>
						</tr>
						<tr style='border-bottom: 1px solid #eee;'>
							<td style='padding: 8px;'><b><a href='https://github.com/luizmoretti/Django_ERP/blob/master/BackEnd/DRF Docs/Django Rest Framework Documentation - Filtering.md'>Django Rest Framework Documentation - Filtering.md</a></b></td>
							<td style='padding: 8px;'>- This code file provides essential guidance on implementing filtering mechanisms within the Django REST Framework (DRF) for the backend architecture<br>- Its primary purpose is to facilitate the customization and restriction of data retrieval, enabling the API to return only relevant subsets of data based on specific criteria<br>- By leveraging filtering strategies, the code supports the overall architectures goal of delivering precise, secure, and efficient data responses tailored to client requests, thereby enhancing the APIs flexibility and usability across the system.</td>
						</tr>
						<tr style='border-bottom: 1px solid #eee;'>
							<td style='padding: 8px;'><b><a href='https://github.com/luizmoretti/Django_ERP/blob/master/BackEnd/DRF Docs/Django Rest Framework Documentation - Settings.md'>Django Rest Framework Documentation - Settings.md</a></b></td>
							<td style='padding: 8px;'>- This documentation file provides an overview of the configuration settings for the Django REST Framework (DRF) within the project<br>- It highlights how the DRFs behavior is governed through a centralized <code>REST_FRAMEWORK</code> namespace in the projects <code>settings.py</code>, enabling consistent customization of core functionalities such as rendering and parsing of API data<br>- Overall, this file serves as a guide for understanding and managing the DRF configuration, ensuring that the API's data serialization, rendering, and parsing behaviors align with the project's architectural standards.</td>
						</tr>
					</table>
				</blockquote>
			</details>
			<!-- templates Submodule -->
			<details>
				<summary><b>templates</b></summary>
				<blockquote>
					<div class='directory-path' style='padding: 8px 0; color: #666;'>
						<code><b>⦿ BackEnd.templates</b></code>
					<!-- emails Submodule -->
					<details>
						<summary><b>emails</b></summary>
						<blockquote>
							<div class='directory-path' style='padding: 8px 0; color: #666;'>
								<code><b>⦿ BackEnd.templates.emails</b></code>
							<!-- purchase_order Submodule -->
							<details>
								<summary><b>purchase_order</b></summary>
								<blockquote>
									<div class='directory-path' style='padding: 8px 0; color: #666;'>
										<code><b>⦿ BackEnd.templates.emails.purchase_order</b></code>
									<table style='width: 100%; border-collapse: collapse;'>
									<thead>
										<tr style='background-color: #f8f9fa;'>
											<th style='width: 30%; text-align: left; padding: 8px;'>File Name</th>
											<th style='text-align: left; padding: 8px;'>Summary</th>
										</tr>
									</thead>
										<tr style='border-bottom: 1px solid #eee;'>
											<td style='padding: 8px;'><b><a href='https://github.com/luizmoretti/Django_ERP/blob/master/BackEnd/templates/emails/purchase_order/new_order.html'>new_order.html</a></b></td>
											<td style='padding: 8px;'>- Generates a professional HTML email template for purchase order notifications, facilitating clear communication between companies and suppliers<br>- It presents order details, product listings, and totals in a visually organized manner, supporting automated email workflows within the broader backend architecture<br>- This template ensures consistent, branded, and easily understandable purchase order correspondence.</td>
										</tr>
									</table>
								</blockquote>
							</details>
							<!-- auth Submodule -->
							<details>
								<summary><b>auth</b></summary>
								<blockquote>
									<div class='directory-path' style='padding: 8px 0; color: #666;'>
										<code><b>⦿ BackEnd.templates.emails.auth</b></code>
									<table style='width: 100%; border-collapse: collapse;'>
									<thead>
										<tr style='background-color: #f8f9fa;'>
											<th style='width: 30%; text-align: left; padding: 8px;'>File Name</th>
											<th style='text-align: left; padding: 8px;'>Summary</th>
										</tr>
									</thead>
										<tr style='border-bottom: 1px solid #eee;'>
											<td style='padding: 8px;'><b><a href='https://github.com/luizmoretti/Django_ERP/blob/master/BackEnd/templates/emails/auth/password_reset_email.html'>password_reset_email.html</a></b></td>
											<td style='padding: 8px;'>- Provides a styled HTML email template for password reset notifications within the backend authentication system<br>- It facilitates secure user-initiated password recovery by delivering a visually consistent and responsive email containing a reset link, integrating seamlessly with the applications URL routing and user account management architecture.</td>
										</tr>
									</table>
								</blockquote>
							</details>
						</blockquote>
					</details>
				</blockquote>
			</details>
			<!-- nginx Submodule -->
			<details>
				<summary><b>nginx</b></summary>
				<blockquote>
					<div class='directory-path' style='padding: 8px 0; color: #666;'>
						<code><b>⦿ BackEnd.nginx</b></code>
					<table style='width: 100%; border-collapse: collapse;'>
					<thead>
						<tr style='background-color: #f8f9fa;'>
							<th style='width: 30%; text-align: left; padding: 8px;'>File Name</th>
							<th style='text-align: left; padding: 8px;'>Summary</th>
						</tr>
					</thead>
						<tr style='border-bottom: 1px solid #eee;'>
							<td style='padding: 8px;'><b><a href='https://github.com/luizmoretti/Django_ERP/blob/master/BackEnd/nginx/nginx.conf'>nginx.conf</a></b></td>
							<td style='padding: 8px;'>- Defines the Nginx server configuration to route incoming HTTP and WebSocket requests to the Django backend, manage static and media assets efficiently, and ensure secure, optimized communication within the overall application architecture<br>- This setup facilitates seamless client-server interactions, supporting real-time features and static content delivery in a scalable, production-ready environment.</td>
						</tr>
					</table>
				</blockquote>
			</details>
		</blockquote>
	</details>
	<!-- .github Submodule -->
	<details>
		<summary><b>.github</b></summary>
		<blockquote>
			<div class='directory-path' style='padding: 8px 0; color: #666;'>
				<code><b>⦿ .github</b></code>
			<!-- workflows Submodule -->
			<details>
				<summary><b>workflows</b></summary>
				<blockquote>
					<div class='directory-path' style='padding: 8px 0; color: #666;'>
						<code><b>⦿ .github.workflows</b></code>
					<table style='width: 100%; border-collapse: collapse;'>
					<thead>
						<tr style='background-color: #f8f9fa;'>
							<th style='width: 30%; text-align: left; padding: 8px;'>File Name</th>
							<th style='text-align: left; padding: 8px;'>Summary</th>
						</tr>
					</thead>
						<tr style='border-bottom: 1px solid #eee;'>
							<td style='padding: 8px;'><b><a href='https://github.com/luizmoretti/Django_ERP/blob/master/.github/workflows/django.yml'>django.yml</a></b></td>
							<td style='padding: 8px;'>- Defines the CI/CD pipeline for the Django ERP project, automating testing, code quality checks, and database migrations upon code pushes or pull requests to main and Dev branches<br>- Ensures consistent environment setup with Docker services for PostgreSQL and Redis, maintaining code standards and verifying application integrity within the overall architecture.</td>
						</tr>
					</table>
				</blockquote>
			</details>
		</blockquote>
	</details>
</details>

---

## 🚀 Getting Started

### 📋 Prerequisites

This project requires the following dependencies:

- **Programming Language:** Python
- **Package Manager:** Pip
- **Container Runtime:** Docker

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

**Using [docker](https://www.docker.com/):**

```sh
❯ docker build -t luizmoretti/Django_ERP .
```
**Using [pip](https://pypi.org/project/pip/):**

```sh
❯ pip install -r BackEnd/requirements.txt
```

### 💻 Usage

Run the project with:

**Using [docker](https://www.docker.com/):**

```sh
docker run -it {image_name}
```
**Using [pip](https://pypi.org/project/pip/):**

```sh
python {entrypoint}
```

### 🧪 Testing

Django_erp uses the {__test_framework__} test framework. Run the test suite with:

**Using [docker](https://www.docker.com/):**

```sh
echo 'INSERT-TEST-COMMAND-HERE'
```
**Using [pip](https://pypi.org/project/pip/):**

```sh
pytest
```

---

## 📈 Roadmap

- [X] **`Task 1`**: <strike>Implement feature one.</strike>
- [ ] **`Task 2`**: Implement feature two.
- [ ] **`Task 3`**: Implement feature three.

---

## 📜 License

Django_erp is protected under the [LICENSE](https://choosealicense.com/licenses) License. For more details, refer to the [LICENSE](https://choosealicense.com/licenses/) file.

---

## ✨ Acknowledgments

- Credit `contributors`, `inspiration`, `references`, etc.

<div align="left"><a href="#top">⬆ Return</a></div>

---
