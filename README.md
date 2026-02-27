# 📰 Capstone News App (Django + DRF)

A role-based news publishing platform built with **Django** and **Django REST Framework (DRF)**.

This project supports:

- **Readers / Journalists / Editors** (role-based access)
- Web editorial workflow (submit → approve/reject → publish)
- Reader subscriptions (publisher + journalist)
- Email notifications to subscribers when an article is approved
- REST API with **JWT authentication**
- Automated tests (including mocked email tests)

---

# 🚀 Features

## 👤 Authentication & Roles
- Custom user model (`CustomUser`)
- Roles stored in DB with capitalized values:
  - `Reader`
  - `Journalist`
  - `Editor`
- Automatic group assignment + permissions (via signals)
- Login / logout using Django built-in auth routes

---

## 🧾 Registration Workflow (Planned Approval System)
- ✅ **Reader** registration is instant:
  - account is active immediately
  - auto-login after registering
- 🕒 **Journalist** and **Editor** registration requires admin approval:
  - account is created as inactive (`is_active=False`)
  - user cannot login until an admin activates the account in Django admin
  - admin has an “Approve selected users” action for quick approvals

**Register URL:**  
`/accounts/register/`

---

## 📰 Article Workflow (Web UI)

### ✍️ Journalist
- Submit a new article from the web UI:
  - `GET/POST /articles/new/`

### ✅ Editor
- Review pending articles in the approval queue:
  - `GET /queue/`
- Approve / reject articles:
  - `POST /queue/<id>/approve/`
  - `POST /queue/<id>/reject/`

### 👀 Reader
- View approved articles in the main list:
  - `GET /`
- View article detail:
  - `GET /articles/<id>/`

---

## 🔔 Subscriptions (Web UI)
Readers can subscribe/unsubscribe directly from the **article detail page**:

- Subscribe to journalist:
  - `POST /articles/<id>/subscribe/journalist/`
- Subscribe to publisher:
  - `POST /articles/<id>/subscribe/publisher/`
- Unsubscribe from journalist:
  - `POST /articles/<id>/unsubscribe/journalist/`
- Unsubscribe from publisher:
  - `POST /articles/<id>/unsubscribe/publisher/`

These subscriptions drive:
- the “subscribed articles” API endpoint
- email notifications on approval

---

## ✉ Email Notifications (Required Feature)
When an editor approves an article, the app emails all readers subscribed to:
- the article’s **publisher**
- and/or the article’s **journalist (author)**

### Development setup
Emails are printed in the terminal using Django’s console backend:

```python
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
DEFAULT_FROM_EMAIL = "noreply@capstonenews.local"
```

---

# 🔌 REST API (Django REST Framework)

The project exposes REST endpoints so users can interact with articles, subscriptions, publishers and newsletters via JSON.

### Authentication
- Session authentication (Browsable API)
- JWT authentication (SimpleJWT)
  - `POST /api/token/`
  - `POST /api/token/refresh/`

---

## API Endpoints

### Articles
```
GET  /api/articles/
POST /api/articles/
GET  /api/articles/<id>/
PUT  /api/articles/<id>/
PATCH /api/articles/<id>/
DELETE /api/articles/<id>/
```

### Subscribed Articles
```
GET /api/articles/subscribed/
```

### Editor Approval (API)
```
GET  /api/articles/pending/
POST /api/articles/<id>/approve/
POST /api/articles/<id>/reject/
```

### Publishers (Read-only)
```
GET /api/publishers/
GET /api/publishers/<id>/
```

### Publisher Subscriptions (Reader)
```
GET  /api/publisher-subscriptions/
POST /api/publisher-subscriptions/
DELETE /api/publisher-subscriptions/<id>/
```

### Journalist Subscriptions (Reader)
```
GET  /api/journalist-subscriptions/
POST /api/journalist-subscriptions/
DELETE /api/journalist-subscriptions/<id>/
```

### Newsletters
```
GET  /api/newsletters/
POST /api/newsletters/
GET  /api/newsletters/<id>/
PUT/PATCH/DELETE /api/newsletters/<id>/manage/
```

### Publisher Memberships (Read-only)
```
GET /api/publisher-memberships/
GET /api/publisher-memberships/<id>/
```

---

# 🧩 What I Implemented (Task Summary)

For this capstone project, I implemented a full web + API news platform including:

- A custom user model with roles (Reader / Journalist / Editor)
- Role-based permissions with group assignment and signal automation
- Web editorial workflow:
  - journalist submission
  - editor approval queue
  - approve/reject actions
- Reader subscription system:
  - subscribe/unsubscribe to journalist and publisher (web UI)
  - API endpoints for subscription management
- Required feature: **email to subscribers on article approval**
- DRF API with JWT authentication:
  - token obtain + refresh
  - CRUD endpoints for articles and newsletters
  - approval endpoints for editors
  - subscribed articles feed
- Automated testing:
  - article API tests
  - mocked tests for email notification logic

---

# 🏗 Architecture Overview

The project is separated into apps by responsibility:

- `accounts/`
  - custom user model
  - registration workflow (Reader instant, Journalist/Editor pending approval)
  - signals for groups/permissions + role group assignment
  - admin approval action
- `news/`
  - web UI pages for articles
  - editor queue, approve/reject
  - subscribe/unsubscribe views
  - email notification service
- `api/`
  - DRF serializers, views, permission classes
  - endpoints for articles, publishers, subscriptions, newsletters, memberships

---

# 📁 Project Structure

```text
capstone_news/
│
├── manage.py
├── requirements.txt
├── README.md
│
├── config/
│   ├── settings.py
│   ├── urls.py
│   └── ...
│
├── accounts/
│   ├── models.py
│   ├── forms.py
│   ├── views.py
│   ├── signals.py
│   ├── admin.py
│   └── migrations/
│
├── news/
│   ├── models.py
│   ├── views.py
│   ├── urls.py
│   ├── services.py
│   └── templates/news/
│
├── api/
│   ├── serializers.py
│   ├── views.py
│   ├── permissions.py
│   ├── urls.py
│   └── tests/
│
├── templates/
│   ├── base.html
│   └── registration/
│       ├── login.html
│       └── register.html
│
└── static/
    └── ...
```

---

# ⚙ Installation

## 1️⃣ Create virtual environment

```bash
python -m venv .venv
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # macOS/Linux
```

## 2️⃣ Install dependencies

```bash
pip install -r requirements.txt
```

## 3️⃣ Run migrations

```bash
python manage.py migrate
```

## 4️⃣ Create admin user (recommended)

```bash
python manage.py createsuperuser
```

## 5️⃣ Run server

```bash
python manage.py runserver
```

---

# ✅ Demo / Marker Testing Flow (Recommended)

1. Start server and login to admin:
   - `/admin/`
2. Create an **Editor** account (or approve one from pending registrations)
3. Register a **Reader** using:
   - `/accounts/register/`
4. Register a **Journalist** using:
   - `/accounts/register/`
5. Approve the Journalist account in admin (activate user)
6. Login as Journalist and submit an article:
   - `/articles/new/`
7. Login as Reader and subscribe to journalist/publisher from article detail
8. Login as Editor and approve the article:
   - `/queue/`
9. Check terminal output for the approval email (console backend)

---

# 🧪 Testing

Run all tests:

```bash
python manage.py test
```

Run only article API tests:

```bash
python manage.py test api.tests.test_article_api
```

Run email notification tests:

```bash
python manage.py test news.tests.test_email_notifications
```

---

# 🧠 Result

This project demonstrates:

- Django web app architecture
- Role-based access control
- Editorial workflow implementation
- DRF API design + JWT authentication
- Subscription-based notification logic
- Unit testing with mocking for side-effects (email)


## MariaDB Configuration

This project is configured to use **MariaDB** instead of SQLite.

1. Create a MariaDB database named `capstone_news` (or set your own value in environment variables).
2. Copy `.env.example` values into your local environment.
3. Run migrations:

```bash
python manage.py makemigrations
python manage.py migrate
```

Environment variables used by the project:

- `DB_NAME`
- `DB_USER`
- `DB_PASSWORD`
- `DB_HOST`
- `DB_PORT`

## Resubmission Notes

- Removed unused placeholder app references (`core` and `integrations`) from `INSTALLED_APPS` so migrations can run correctly.
- Replaced the SQLite database configuration with a MariaDB configuration.
- Added `PyMySQL` in `requirements.txt` and configured it as the MySQL/MariaDB driver.
