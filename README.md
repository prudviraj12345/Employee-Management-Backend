<div align="center">

# 📧 Enterprise Email Portal

### Employee Management & Communication Backend

[![Django](https://img.shields.io/badge/Django-5.2-092E20?style=for-the-badge&logo=django&logoColor=white)](https://www.djangoproject.com/)
[![DRF](https://img.shields.io/badge/DRF-3.17-ff1709?style=for-the-badge&logo=django&logoColor=white)](https://www.django-rest-framework.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Supabase-4169E1?style=for-the-badge&logo=postgresql&logoColor=white)](https://supabase.com/)
[![Python](https://img.shields.io/badge/Python-3.12+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org/)
[![Render](https://img.shields.io/badge/Deploy-Render-46E3B7?style=for-the-badge&logo=render&logoColor=white)](https://render.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge)](LICENSE)

A full-stack **Employee Management & Email Communication** platform built with Django REST Framework. Manage your organization's workforce, departments, and outbound email communications — all from a single, beautifully designed console with a complete audit trail.

### 🌍 [Live Demo →](http://23.20.228.176/)

| | |
|---|---|
| **🔗 URL** | **http://23.20.228.176/** |
| **👤 Username** | `admin12123` |
| **🔑 Password** | `passward123` |

---

[Features](#-features) · [Architecture](#-architecture) · [Quick Start](#-quick-start) · [API Reference](#-api-reference) · [Deployment](#-deployment)

</div>

---

## ✨ Features

<table>
<tr>
<td width="50%">

### 🔐 Authentication & Security
- Token-based authentication (DRF `TokenAuthentication`)
- Session & Basic Auth support
- Admin-only login enforcement (`is_staff` check)
- Profile management (view/update username, email, display name)
- Secure password change with token rotation

</td>
<td width="50%">

### 👥 Employee Management
- Full CRUD with `ModelViewSet`
- Business ID format enforcement (`EMP001` – `EMP999999`)
- Comprehensive field-level & cross-field validation
- Phone, email, and employee ID uniqueness checks
- Designation choices (SE, SSE, Manager, HR, Intern, Other)

</td>
</tr>
<tr>
<td width="50%">

### 🏢 Department Management
- Full CRUD operations
- Unique department name constraint
- `PROTECT` foreign key — prevents deleting departments with active employees
- Auto-timestamped records

</td>
<td width="50%">

### 📬 Email Service
- Send emails via SMTP (Gmail) with attachment support
- Email template CRUD for reusable messages
- Auto status tracking (`Pending → Sending → Sent / Failed`)
- Retry count tracking
- Console fallback when SMTP credentials are missing

</td>
</tr>
<tr>
<td width="50%">

### 📜 Email History & Audit Trail
- Automatic history logging on every email dispatch
- Tracks: employee, recipient, subject, message, status, retry count, timestamp
- Full audit trail for compliance & reporting

</td>
<td width="50%">

### 📊 Dashboard & Analytics
- Public stats endpoint (employee count, emails sent today, delivery rate)
- Email diagnostics endpoint (`/api/email-check/`)
- Real-time SMTP connection health monitoring
- Beautiful single-page frontend with 8 integrated views

</td>
</tr>
</table>

---

## 🏗 Architecture

```
Employee-Management-Backend/
│
├── config/                     # Django project configuration
│   ├── settings.py             # Settings with env-based config
│   ├── urls.py                 # Root URL routing
│   ├── wsgi.py                 # WSGI entry point
│   └── asgi.py                 # ASGI entry point
│
├── authentication/             # 🔐 Auth module
│   ├── models.py               # Uses Django's built-in User model
│   ├── serializers.py          # Login, Profile, ChangePassword serializers
│   ├── views.py                # login, profile, change_password, public_stats, email_check
│   └── urls.py                 # /api/login/, /api/profile/, etc.
│
├── employee/                   # 👥 Employee module
│   ├── models.py               # Employee model with validators & indexes
│   ├── serializers.py          # Rich validation (regex, uniqueness, cross-field)
│   ├── views.py                # ModelViewSet with select_related optimization
│   └── urls.py                 # /api/employees/
│
├── department/                 # 🏢 Department module
│   ├── models.py               # Department model (unique name)
│   ├── serializers.py          # Department serializer with validation
│   ├── views.py                # ModelViewSet
│   └── urls.py                 # /api/departments/
│
├── email_service/              # 📬 Email module
│   ├── models.py               # EmailLog + EmailTemplate models
│   ├── serializers.py          # Email serializers
│   ├── views.py                # Send emails, auto-history, attachment support
│   └── urls.py                 # /api/emails/, /api/email-templates/
│
├── history/                    # 📜 History module
│   ├── models.py               # EmailHistory model
│   ├── serializers.py          # History serializer
│   ├── views.py                # Read-only viewset
│   └── urls.py                 # /api/history/
│
├── templates/                  # 🎨 Frontend (Django templates)
│   ├── index.html              # SPA-style entry point
│   ├── includes/               # Shared components (head, navbar, sidebar, modals, scripts)
│   └── views/                  # Page views (dashboard, employees, departments, etc.)
│
├── gunicorn.conf.py            # Production WSGI server config
├── requirements.txt            # Python dependencies
├── manage.py                   # Django management CLI
└── .env.example                # Environment variable template
```

### Data Model Relationships

```mermaid
erDiagram
    Department ||--o{ Employee : "has many"
    Employee ||--o{ EmailLog : "receives"
    Employee ||--o{ EmailHistory : "tracked in"

    Department {
        int id PK
        string department_name UK
        text description
        datetime created_at
    }

    Employee {
        int id PK
        string employee_id UK "EMP001 format"
        string first_name
        string last_name
        string email UK
        string phone
        int department_id FK
        string designation "SE|SSE|MGR|HR|INT|OTH"
        decimal salary
        date joining_date
        boolean status "Active/Inactive"
        datetime created_at
        datetime updated_at
    }

    EmailLog {
        int id PK
        int employee_id FK
        string recipient_email
        string subject
        text message
        string status "Pending|Sending|Sent|Failed"
        int retry_count
        datetime created_at
        datetime sent_at
    }

    EmailTemplate {
        int id PK
        string title
        string subject
        text message
        datetime created_at
        datetime updated_at
    }

    EmailHistory {
        int id PK
        int employee_id FK
        string recipient_email
        string subject
        text message
        string status "Sent|Failed"
        int retry_count
        datetime sent_at
    }
```

---

## 🚀 Quick Start

### Prerequisites

| Requirement | Version |
|------------|---------|
| Python | 3.12+ |
| pip | Latest |
| PostgreSQL | 15+ (or use Supabase) |
| Git | Latest |

### 1️⃣ Clone the Repository

```bash
git clone https://github.com/your-username/Employee-Management-Backend.git
cd Employee-Management-Backend
```

### 2️⃣ Create & Activate Virtual Environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

### 3️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

### 4️⃣ Configure Environment Variables

```bash
cp .env.example .env
```

Edit `.env` with your actual values:

```env
# Django
SECRET_KEY=your-super-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database (Supabase PostgreSQL)
DATABASE_URL=postgresql://postgres.[ref]:[password]@aws-0-[region].pooler.supabase.com:6543/postgres?sslmode=require

# Email (Gmail SMTP)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
DEFAULT_FROM_EMAIL=your-email@gmail.com
```

> **💡 Tip:** For Gmail, use an [App Password](https://support.google.com/accounts/answer/185833) instead of your account password.

### 5️⃣ Run Migrations & Create Superuser

```bash
python manage.py migrate
python manage.py createsuperuser
```

### 6️⃣ Start the Development Server

```bash
python manage.py runserver
```

Open **http://127.0.0.1:8000/** to view the Enterprise Email Portal.

---

## 📖 API Reference

> **Base URL:** `http://127.0.0.1:8000/api/`
>
> All endpoints (except login, public-stats, and email-check) require **Token Authentication**.
> Include the header: `Authorization: Token <your-token>`

### 🔐 Authentication

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| `POST` | `/api/login/` | ❌ | Admin login → returns auth token |
| `GET` | `/api/profile/` | ✅ | Get current user profile |
| `PUT/PATCH` | `/api/profile/` | ✅ | Update username, email, display name |
| `POST` | `/api/change-password/` | ✅ | Change password (rotates token) |
| `GET` | `/api/public-stats/` | ❌ | Dashboard stats (employees, emails today, delivery rate) |
| `GET` | `/api/email-check/` | ❌ | SMTP configuration diagnostics |

<details>
<summary><strong>📝 Login Example</strong></summary>

**Request:**
```http
POST /api/login/
Content-Type: application/json

{
    "username": "admin",
    "password": "admin123"
}
```

**Response:**
```json
{
    "success": true,
    "message": "Login Successful",
    "token": "a1b2c3d4e5f6...",
    "profile": {
        "username": "admin",
        "email": "admin@gmail.com",
        "display_name": "Admin"
    }
}
```

</details>

---

### 👥 Employees

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/employees/` | List all employees |
| `POST` | `/api/employees/` | Create a new employee |
| `GET` | `/api/employees/{id}/` | Retrieve employee details |
| `PUT` | `/api/employees/{id}/` | Full update |
| `PATCH` | `/api/employees/{id}/` | Partial update |
| `DELETE` | `/api/employees/{id}/` | Delete employee |

<details>
<summary><strong>📝 Create Employee Example</strong></summary>

**Request:**
```http
POST /api/employees/
Authorization: Token a1b2c3d4e5f6...
Content-Type: application/json

{
    "employee_id": "EMP101",
    "first_name": "Rahul",
    "last_name": "Sharma",
    "email": "rahul@gmail.com",
    "phone": "9876543210",
    "department": 1,
    "designation": "SE",
    "salary": 50000.00,
    "joining_date": "2025-01-15"
}
```

**Validation Rules:**
| Field | Rule |
|-------|------|
| `employee_id` | Must match `EMP` + 3-6 digits (e.g., `EMP001`) |
| `first_name` / `last_name` | Min 2 chars, no digits |
| `email` | Valid format, unique |
| `phone` | 10-15 digits, optional `+` prefix, unique |
| `salary` | Must be positive |
| `joining_date` | Cannot be in the future |
| `designation` | One of: `SE`, `SSE`, `MGR`, `HR`, `INT`, `OTH` |

</details>

---

### 🏢 Departments

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/departments/` | List all departments |
| `POST` | `/api/departments/` | Create department |
| `GET` | `/api/departments/{id}/` | Retrieve department |
| `PUT` | `/api/departments/{id}/` | Update department |
| `DELETE` | `/api/departments/{id}/` | Delete department (fails if employees exist) |

<details>
<summary><strong>📝 Create Department Example</strong></summary>

```http
POST /api/departments/
Authorization: Token a1b2c3d4e5f6...
Content-Type: application/json

{
    "department_name": "Human Resources",
    "description": "Handles employee recruitment and management."
}
```

</details>

---

### 📬 Email Service

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/emails/` | List all sent emails |
| `POST` | `/api/emails/` | Send an email (with optional attachment) |
| `GET` | `/api/emails/{id}/` | Retrieve email details |
| `GET` | `/api/email-templates/` | List email templates |
| `POST` | `/api/email-templates/` | Create reusable email template |
| `PUT` | `/api/email-templates/{id}/` | Update template |
| `DELETE` | `/api/email-templates/{id}/` | Delete template |

<details>
<summary><strong>📝 Send Email Example</strong></summary>

```http
POST /api/emails/
Authorization: Token a1b2c3d4e5f6...
Content-Type: multipart/form-data

employee: 1
recipient_email: rahul@gmail.com
subject: Welcome to ABC Company
message: Welcome aboard, Rahul! We're excited to have you.
attachment: (optional file upload)
```

**Status Flow:** `Pending → Sent` or `Pending → Failed`

> History is **automatically created** after every email dispatch.

</details>

---

### 📜 Email History

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/history/` | View complete email audit trail |

**Response includes:** Employee, recipient email, subject, message, status, retry count, sent timestamp.

---

## 🌐 Deployment

### Deploy to Render

This project is production-ready with Gunicorn configuration optimized for Render's free tier.

```python
# gunicorn.conf.py
workers = 1          # Free-tier Render (512 MB RAM)
threads = 4          # Concurrent requests within single worker
timeout = 120        # 2-minute timeout for batch email operations
```

**Steps:**

1. Push your code to GitHub
2. Create a new **Web Service** on [Render](https://render.com/)
3. Connect your repository
4. Set the following:

| Setting | Value |
|---------|-------|
| **Build Command** | `pip install -r requirements.txt` |
| **Start Command** | `gunicorn config.wsgi:application -c gunicorn.conf.py` |

5. Add all environment variables from `.env.example` in Render's **Environment** tab
6. Deploy! 🚀

---

## 🛠 Tech Stack

| Layer | Technology |
|-------|-----------|
| **Framework** | Django 5.2 |
| **REST API** | Django REST Framework 3.17 |
| **Database** | PostgreSQL (Supabase) |
| **DB Driver** | psycopg 3.3 |
| **DB URL Parser** | dj-database-url |
| **WSGI Server** | Gunicorn 21.2 |
| **Email** | Django SMTP (Gmail) |
| **Auth** | Token Authentication |
| **Frontend** | Django Templates + Bootstrap + Lucide Icons |

---

## 🔧 Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `SECRET_KEY` | ✅ | Insecure fallback | Django secret key |
| `DEBUG` | ❌ | `True` | Debug mode |
| `ALLOWED_HOSTS` | ❌ | `*` | Comma-separated allowed hosts |
| `DATABASE_URL` | ✅ | Supabase fallback | PostgreSQL connection string |
| `EMAIL_HOST` | ❌ | `smtp.gmail.com` | SMTP server host |
| `EMAIL_PORT` | ❌ | `587` | SMTP port |
| `EMAIL_USE_TLS` | ❌ | `True` | Enable TLS |
| `EMAIL_HOST_USER` | ✅ | — | SMTP username/email |
| `EMAIL_HOST_PASSWORD` | ✅ | — | SMTP app password |
| `DEFAULT_FROM_EMAIL` | ❌ | `EMAIL_HOST_USER` | Default sender address |

---

## 📂 Frontend Views

The application includes a single-page frontend with **8 integrated views**:

| # | View | Description |
|---|------|-------------|
| 1 | **Dashboard** | Overview cards, stats, and quick actions |
| 2 | **Employees** | Employee table with CRUD operations |
| 3 | **Departments** | Department management |
| 4 | **Email Templates** | Create & manage reusable email templates |
| 5 | **Send Email** | Compose and send emails with attachments |
| 6 | **Email History** | Complete audit trail of all dispatched emails |
| 7 | **Reports** | Analytical reports and insights |
| 8 | **Settings** | Application configuration |

---

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. **Fork** the repository
2. **Create** your feature branch (`git checkout -b feature/amazing-feature`)
3. **Commit** your changes (`git commit -m 'Add amazing feature'`)
4. **Push** to the branch (`git push origin feature/amazing-feature`)
5. **Open** a Pull Request

---

## 📄 License

This project is open source and available under the [MIT License](LICENSE).

---

<div align="center">

**Built with ❤️ using Django & Django REST Framework**

</div>
