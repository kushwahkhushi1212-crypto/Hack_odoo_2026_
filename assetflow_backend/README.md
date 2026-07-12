# AssetFlow — Django Backend

A Django + Django REST Framework API backend built to match the AssetFlow
frontend (login, dashboard, organization setup, asset directory,
allocation & transfer, resource booking, maintenance kanban, audits,
reports, notifications).

## 1. Setup

```bash
python -m venv venv
source venv/bin/activate        # venv\Scripts\activate on Windows

pip install -r requirements.txt

cp .env.example .env             # edit SECRET_KEY etc.

python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser

python manage.py runserver
```

The API is served at `http://127.0.0.1:8000/api/`, admin at `/admin/`.

> Note: `accounts.User` and `organization.Department` reference each other
> (a user has a department; a department has a head). `makemigrations`
> will correctly stage this as a normal two-app circular dependency —
> just run it once, no manual migration editing needed.

## 2. Auth

JWT-based (djangorestframework-simplejwt), matching the email/password
AssetFlow login form.

| Method | Endpoint | Notes |
|---|---|---|
| POST | `/api/auth/login/` | `{email, password}` → `{access, refresh, user}` |
| POST | `/api/auth/refresh/` | `{refresh}` → new `access` |
| POST | `/api/auth/signup/` | Public. Creates an employee profile with role `employee` (admin access is granted later by an org admin — see the note on the login screen) |
| GET/PATCH | `/api/auth/me/` | Current user's own profile |
| GET/POST/PATCH/DELETE | `/api/auth/employees/` | Employee directory (read: any signed-in user; write: admin only) |
| PATCH | `/api/auth/employees/<id>/role/` | Admin promotes/demotes a role |

Send `Authorization: Bearer <access>` on every other request.

## 3. Feature endpoints

| Screen | Base path |
|---|---|
| Organization Setup — Departments | `/api/org/departments/` |
| Organization Setup — Categories | `/api/org/categories/` |
| Asset Directory | `/api/assets/assets/` (+ `/assets/<id>/history/`) |
| Allocation & Transfer | `/api/transfers/requests/` (+ `/approve/`, `/reject/`) |
| Resource Booking — resources | `/api/bookings/resources/` |
| Resource Booking — bookings | `/api/bookings/bookings/` (+ `/cancel/`, `/week/`) |
| Maintenance kanban | `/api/maintenance/tickets/` (+ `/board/`, `/<id>/move/`) |
| Asset Audit | `/api/audits/cycles/` (+ `/<id>/close/`, `/<id>/discrepancy-report/`), `/api/audits/items/` (+ `/<id>/verify/`) |
| Reports | `/api/reports/dashboard/`, `/utilization/`, `/maintenance-frequency/`, `/most-used/`, `/idle/` |
| Notifications | `/api/notifications/notifications/` (+ `/<id>/read/`, `/read-all/`, `/unread-count/`) |

## 4. Key business rules encoded in the backend

- **Allocation & Transfer**: an allocated asset can never be re-assigned by
  simply editing the asset — only a `TransferRequest` that an admin
  approves moves `Asset.current_holder`, and every approval writes an
  `AllocationHistory` row (return + allocate) for the history panel.
- **Resource Booking**: a new booking that overlaps an existing
  *confirmed* booking on the same resource is stored as `conflict`
  instead of silently double-booking, matching the dashed conflict slot
  in the UI.
- **Maintenance kanban**: cards can only move along the allowed
  pending → approved → assigned → in progress → resolved path (or one
  step back). Approving sets the linked asset to `maintenance`;
  resolving returns it to `available`.
- **Audit**: closing a cycle requires every asset row to be verified
  first, and automatically compiles the missing/damaged rows into a
  discrepancy report.
- **Notifications**: a single `notify()` helper (`notifications/services.py`)
  is called from transfers/bookings/maintenance/audits so the activity
  log/notification screen stays populated without those apps needing to
  import each other's serializers.
- **Reports**: computed live from the other apps' data (no duplicate
  reporting tables) — utilization %, maintenance frequency by month,
  most-used assets/resources, and idle-asset detection.

## 5. Project layout

```
assetflow_backend/
├── assetflow_backend/   # settings, root urls
├── accounts/             # custom User (employee profile), auth, roles
├── organization/         # Departments, Categories
├── assets/                # Asset directory, allocation history
├── transfers/             # Allocation & transfer request workflow
├── bookings/               # Bookable resources + booking calendar
├── maintenance/            # Maintenance kanban tickets
├── audits/                 # Audit cycles + per-asset verification
├── notifications/          # Activity log / notification feed
└── reports/                 # Dashboard stats + analytics (no models)
```
