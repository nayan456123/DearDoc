# Lucent Sync

Lucent Sync is a local-first telehealth hackathon product built with Django REST and React.

The old operations-heavy hospital dashboard was removed. The product is now focused on one doctor, one patient journey, faster booking, live consultation, and one standout feature called `PulseMatch Copilot`.

## What This Product Is

Lucent Sync is a two-sided telehealth app:

- `Doctor side`: create time slots, manage appointments in a kanban flow, launch live sessions
- `Patient side`: describe symptoms, get a smart triage brief, book a slot, join the consultation

This is meant for local demo testing first.

## Main Innovation

### `PulseMatch Copilot`

This is the hackathon differentiator.

Before a patient books, PulseMatch reads the concern and symptoms in plain language and generates:

- urgency level
- triage score
- specialty hint
- short doctor-facing summary
- pre-call checklist
- suggested appointment slots

It is not a generic theme change or dashboard reskin. It changes how booking and consultation prep work inside the product.

## What Was Removed

The earlier product direction had too much enterprise/operations overhead. These ideas were removed from the main experience:

- command-center style ops framing
- runway screen
- clinical network screen
- extra admin-style control surface
- legacy copied-site feel

The doctor now acts as the operational owner inside the app instead of using a separate admin panel.

## What Was Delivered

### Backend

- Django REST API
- SQLite database
- token authentication
- doctor and patient roles only
- appointment slot creation
- smart booking flow
- kanban-ready appointment statuses
- local WebRTC signaling endpoints
- demo seed command

### Frontend

- React + Vite app
- full UI overhaul
- role-based login
- doctor dashboard
- patient dashboard
- live meeting room
- lighter, cleaner, more product-focused visual system
- responsive layout tuned for laptop and small-screen usage

## Product Flow

### Doctor

- logs in
- creates availability slots
- sees booked requests in kanban columns
- confirms or advances appointment status
- opens the meeting room and starts the call

### Patient

- logs in
- writes concern, symptoms, and notes
- gets PulseMatch analysis
- books one of the available slots
- joins the meeting when the doctor confirms

## Roles And Demo Accounts

- `doctor.rao` / `Doctor@123`
- `patient.asha` / `Patient@123`
- `patient.rohan` / `Patient@123`

## Tech Stack

- Backend: Django, Django REST Framework, django-cors-headers
- Frontend: React 19, React Router, Vite
- Database: SQLite
- Auth: DRF token auth
- Realtime calling: browser WebRTC + Django polling/signaling

## Project Structure

```text
LUCENT/
|-- backend/
|   |-- config/
|   |-- operations/
|   |   |-- management/commands/seed_demo.py
|   |   |-- migrations/
|   |   |-- admin.py
|   |   |-- models.py
|   |   |-- serializers.py
|   |   |-- tests.py
|   |   |-- urls.py
|   |   `-- views.py
|   `-- manage.py
|-- frontend/
|   |-- src/
|   |   |-- components/
|   |   |-- lib/
|   |   |-- pages/
|   |   |-- App.jsx
|   |   |-- index.css
|   |   `-- main.jsx
|   |-- package.json
|   `-- vite.config.js
|-- package.json
|-- requirements.txt
`-- README.md
```

## Main Screens

- `Login`: choose doctor or patient flow with demo credentials
- `Doctor Dashboard`: create slots, manage the kanban, review PulseMatch briefs
- `Patient Dashboard`: generate triage preview, book slots, track meetings
- `Meeting Room`: test local video/audio consultation with WebRTC

## API Overview

Base URL:

`http://127.0.0.1:8000/api/`

Main endpoints:

- `POST /api/auth/login/`
- `POST /api/auth/logout/`
- `GET /api/auth/me/`
- `GET /api/doctor/dashboard/`
- `GET /api/patient/dashboard/`
- `POST /api/triage/preview/`
- `GET /api/slots/`
- `POST /api/slots/`
- `GET /api/appointments/`
- `POST /api/appointments/request/`
- `GET /api/appointments/<id>/`
- `PATCH /api/appointments/<id>/status/`
- `GET /api/appointments/<id>/signals/`
- `POST /api/appointments/<id>/signals/`

## How To Run Locally

### 1. Install backend dependencies

```powershell
python -m pip install -r requirements.txt
```

### 2. Install frontend dependencies

```powershell
npm --prefix frontend install
```

### 3. Create a fresh SQLite database

```powershell
npm run migrate
```

### 4. Seed demo users and appointments

```powershell
npm run seed
```

### 5. Start Django

```powershell
npm run backend
```

Backend:

`http://127.0.0.1:8000`

### 6. Start React in a second terminal

```powershell
npm run frontend
```

Frontend:

`http://127.0.0.1:5173`

## How To Test The Product

### Basic app test

1. Open `http://127.0.0.1:5173`
2. Log in as doctor or patient
3. Check that dashboards load
4. As doctor, add an availability slot
5. As patient, generate a PulseMatch brief and book a slot

### Full local WebRTC test

1. Start backend and frontend
2. Open one browser window as `doctor.rao`
3. Open another browser window or incognito window as `patient.asha`
4. On patient side, generate a triage brief and book a slot
5. On doctor side, refresh and move the appointment to `confirmed`
6. Open the same meeting from both sides
7. Allow camera and microphone access in both browsers
8. Doctor clicks `Launch call`
9. Patient clicks `Enable camera` / joins ready
10. Verify that both local and remote video streams connect

## Do You Need Hosting To Test This?

No, not for the first demo.

Localhost is enough for:

- login flow
- PulseMatch booking flow
- doctor kanban
- local WebRTC testing

## What You Would Need For Internet/Remote Testing Later

If you want to test across different devices or networks later, you will usually need:

- hosted frontend
- hosted Django backend
- HTTPS
- a more durable signaling setup
- TURN server for reliable WebRTC across real networks/firewalls

The current version is intentionally optimized for local-first demo testing.

## Available Scripts

From the repo root:

- `npm run backend`
- `npm run frontend`
- `npm run migrate`
- `npm run seed`
- `npm run test:backend`
- `npm run lint`
- `npm run build`

## Verification Completed

The current code has been verified with:

```powershell
python backend/manage.py check
python backend/manage.py test operations
npm --prefix frontend run lint
npm --prefix frontend run build
```

## Notes

- `backend/db.sqlite3` is ignored so the repo stays fresh
- the current WebRTC implementation is for demo/local validation first
- the doctor is the main operator inside the product, so there is no extra admin product surface
