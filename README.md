# Lucent Care Operations

This repo has been rebuilt from a static clone into a full-stack telehealth operations workspace:

- `backend/`: Django REST API with SQLite
- `frontend/`: React + Vite application with a complete UI overhaul

## Stack

- Django 6
- Django REST Framework
- SQLite
- React 19
- Vite

## Demo Accounts

- Operations lead: `ops.lead` / `CommandCenter@123`
- Clinician: `doctor.rao` / `Doctor@123`

## Local Setup

1. Install Python dependencies:
   `python -m pip install -r requirements.txt`
2. Install frontend dependencies:
   `npm --prefix frontend install`
3. Apply migrations:
   `npm run migrate`
4. Seed demo data:
   `npm run seed`

## Run Locally

Backend:

`npm run backend`

Frontend:

`npm run frontend`

The frontend runs on `http://127.0.0.1:5173` and proxies `/api` requests to Django on `http://127.0.0.1:8000`.

## Verification

- Backend checks: `python backend/manage.py check`
- Backend tests: `python backend/manage.py test`
- Frontend lint: `npm run lint`
- Frontend build: `npm run build`
