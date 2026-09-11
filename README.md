# Developer API Platform

A production-style Developer API Platform where users can create projects, generate API keys, access APIs, monitor requests, configure webhooks, and view usage analytics through a modern React dashboard.

## Features

- 🔐 **Authentication**: JWT with HttpOnly cookies for secure dashboard access
- 🔑 **API Key Management**: Generate, revoke, and rotate API keys with scopes
- ⚡ **Rate Limiting**: Redis-based rate limiting with configurable limits
- 📊 **Request Logging**: All requests logged with full metadata
- 📈 **Analytics Dashboard**: Visualize usage patterns and performance metrics
- 🔗 **Webhooks**: Event-driven webhooks with retry logic
- 🎨 **React Dashboard**: Modern, responsive dashboard built with TypeScript

## Tech Stack

### Backend
- Django 4.2
- Django REST Framework
- PostgreSQL
- Redis
- Celery
- JWT Authentication

### Frontend
- React 18
- TypeScript
- TanStack Query
- Tailwind CSS
- shadcn/ui
- Recharts

## Project Structure
api-platform/
├── backend/
│ ├── apps/
│ │ ├── accounts/ # User authentication
│ │ ├── projects/ # Project management
│ │ ├── api_keys/ # API key management
│ │ ├── gateway/ # API gateway & middleware
│ │ ├── logging/ # Request logging & analytics
│ │ └── common/ # Shared utilities
│ ├── config/
│ │ └── settings/ # Environment-specific settings
│ ├── requirements/ # Python dependencies
│ └── manage.py
├── frontend/ # React dashboard 
├── .github/ # GitHub Actions workflows
└── README.md

## Quick Start

### Prerequisites
- Python 3.10+
- PostgreSQL
- Redis
- Node.js 18+ (for frontend)

### Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/api-platform.git
   cd api-platform

2.Create virtual environment

bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate   

3.Install dependencies

bash
pip install -r requirements/development.txt

4.Configure environment

bash
cp .env.example .env
# Edit .env with your database credentials

5.Setup database

bash
python manage.py makemigrations
python manage.py migrate
python manage.py seed_apis  # Seed predefined APIs
python manage.py createsuperuser
Run development server

6.Run develoment server

python manage.py runserver

7.Access the application

API: http://localhost:8000

Admin: http://localhost:8000/admin

API Documentation: http://localhost:8000/api/docs/

Testing

# Run tests
pytest

# Run tests with coverage
pytest --cov=apps

# Run specific test file
pytest apps/accounts/tests.py

API Documentation

Once the server is running, visit:

Swagger UI: http://localhost:8000/api/docs/

OpenAPI Schema: http://localhost:8000/api/schema/

Development Phases
✅ Phase 1: Foundation (Authentication, Projects, API Keys)

✅ Phase 2: Gateway & Request Logging

✅ Phase 3: Rate Limiting & Analytics

✅ Phase 4: React Dashboard

✅ Phase 5: Webhooks

✅ Phase 6: Testing

Contributing
Fork the repository

Create a feature branch

Commit your changes

Push to the branch

Create a Pull Request

License
MIT License