# Lucent Care Operations

Lucent Care Operations is a Django REST + React rebuild of the previous static telemedicine clone. The original bundled website and proxy-server setup were removed and replaced with a source-based full-stack application that is easier to maintain, extend, and deploy.

## What Was Delivered

This project now includes:

- A Django REST backend with SQLite
- A React frontend built with Vite
- Token-based authentication
- A complete UI overhaul with a more serious operations-console structure
- Demo telehealth operations data through a seed command
- A cleaner repo structure without the old cloned website bundle

## Product Direction

The earlier version behaved like a copied static site. This rebuild changes the product into an operations-focused care platform with a more structured and serious layout.

The new frontend is organized around:

- Command Center
- Patient Ledger
- Appointment Runway
- Clinical Network
- Intake Board

## Tech Stack

- Backend: Django 6, Django REST Framework, django-cors-headers
- Database: SQLite
- Frontend: React 19, React Router, Vite
- Package manager: npm

## Project Structure

```text
LUCENT/
├── backend/
│   ├── config/
│   ├── operations/
│   │   ├── management/commands/seed_demo.py
│   │   ├── migrations/
│   │   ├── models.py
│   │   ├── serializers.py
│   │   ├── urls.py
│   │   └── views.py
│   └── manage.py
├── frontend/
│   ├── src/
│   │   ├── lib/api.js
│   │   ├── App.jsx
│   │   ├── index.css
│   │   └── main.jsx
│   ├── package.json
│   └── vite.config.js
├── package.json
├── requirements.txt
└── README.md
```

## Main Features

### Backend

- Token login and logout endpoints
- Authenticated `me` endpoint
- Dashboard overview endpoint
- List endpoints for patients, appointments, clinicians, intake requests, and tasks
- Update endpoints for intake status and task status
- SQLite-backed data model for clinics, clinicians, patients, appointments, intake requests, operational signals, and tasks
- Demo seed command for quick local setup

### Frontend

- Login screen with demo account shortcuts
- Protected application shell
- Left navigation rail instead of a marketing-style navbar
- Data-first operational dashboard instead of the previous site-like landing layout
- Responsive layouts for desktop and mobile
- Searchable patient ledger
- Structured intake workflow board
- Task completion actions and live API-backed updates

## API Overview

Base URL during local development:

`http://127.0.0.1:8000/api/`

Main endpoints:

- `POST /api/auth/login/`
- `POST /api/auth/logout/`
- `GET /api/auth/me/`
- `GET /api/overview/`
- `GET /api/patients/`
- `GET /api/appointments/`
- `GET /api/clinicians/`
- `GET /api/intake/`
- `PATCH /api/intake/<id>/`
- `GET /api/tasks/`
- `PATCH /api/tasks/<id>/`

## Demo Accounts

- Operations lead: `ops.lead` / `CommandCenter@123`
- Doctor: `doctor.rao` / `Doctor@123`
- Doctor: `doctor.kapoor` / `Doctor@123`

## How To Run

### 1. Install backend dependencies

```powershell
python -m pip install -r requirements.txt
```

### 2. Install frontend dependencies

```powershell
npm --prefix frontend install
```

### 3. Create the SQLite database

```powershell
npm run migrate
```

### 4. Seed demo data

```powershell
npm run seed
```

### 5. Start the backend

```powershell
npm run backend
```

Backend runs at:

`http://127.0.0.1:8000`

### 6. Start the frontend

Open a second terminal and run:

```powershell
npm run frontend
```

Frontend runs at:

`http://127.0.0.1:5173`

The Vite dev server proxies `/api` requests to Django automatically.

## Available Scripts

From the repo root:

- `npm run backend`
- `npm run frontend`
- `npm run migrate`
- `npm run seed`
- `npm run test:backend`
- `npm run lint`
- `npm run build`

## Verification

The current rebuild has been verified with:

```powershell
python backend/manage.py check
npm run test:backend
npm run lint
npm run build
```

## Notes About Cleanup

The following legacy items were removed from the repo:

- Old static cloned frontend bundle
- Proxy-based `server.js`
- Old root `index.html`
- Cloned asset folders from the previous site version
- Committed SQLite database file so the repo stays clean and reproducible

This means the repository now contains source code and setup instructions instead of copied build artifacts.
