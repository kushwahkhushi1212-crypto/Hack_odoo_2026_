-- =============================================================================
-- AssetFlow — database schema (PostgreSQL)
--
-- This is a hand-written mirror of the Django models in the backend project
-- (accounts, organization, assets, transfers, bookings, maintenance, audits,
-- notifications). In normal use you never run this file directly — Django's
-- `makemigrations` / `migrate` generate and apply the real migrations. This
-- script exists for ER-diagramming, manual DB provisioning, or onboarding
-- someone who wants to see the whole schema in one place.
--
-- NOT included here (Django/contrib manages these automatically):
--   django_migrations, django_content_type, django_session, django_admin_log,
--   auth_group, auth_permission, auth_group_permissions
-- `notifications_notification.content_type_id` still references
-- django_content_type(id) below since it's a real generic FK.
-- =============================================================================

-- Safe re-run in dev: drop in FK-dependency order.
DROP TABLE IF EXISTS notifications_notification CASCADE;
DROP TABLE IF EXISTS audits_audititem CASCADE;
DROP TABLE IF EXISTS audits_auditcycle_auditors CASCADE;
DROP TABLE IF EXISTS audits_auditcycle CASCADE;
DROP TABLE IF EXISTS maintenance_maintenancestatuslog CASCADE;
DROP TABLE IF EXISTS maintenance_maintenanceticket CASCADE;
DROP TABLE IF EXISTS bookings_booking CASCADE;
DROP TABLE IF EXISTS bookings_bookableresource CASCADE;
DROP TABLE IF EXISTS transfers_transferrequest CASCADE;
DROP TABLE IF EXISTS assets_assetusageevent CASCADE;
DROP TABLE IF EXISTS assets_allocationhistory CASCADE;
DROP TABLE IF EXISTS assets_asset CASCADE;
DROP TABLE IF EXISTS accounts_user_user_permissions CASCADE;
DROP TABLE IF EXISTS accounts_user_groups CASCADE;
DROP TABLE IF EXISTS accounts_user CASCADE;
DROP TABLE IF EXISTS organization_department CASCADE;
DROP TABLE IF EXISTS organization_category CASCADE;

-- =============================================================================
-- organization — Departments & Categories
-- =============================================================================

CREATE TABLE organization_category (
    id              BIGSERIAL PRIMARY KEY,
    name            VARCHAR(100) NOT NULL UNIQUE,
    description     TEXT NOT NULL DEFAULT '',
    is_active       BOOLEAN NOT NULL DEFAULT TRUE,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- department.head and department.parent both point at tables created later
-- (accounts_user, and itself) — declared with ALTER TABLE further down to
-- keep the accounts <-> organization circular reference straightforward.
CREATE TABLE organization_department (
    id              BIGSERIAL PRIMARY KEY,
    name            VARCHAR(100) NOT NULL UNIQUE,
    code            VARCHAR(20) NOT NULL UNIQUE,
    head_id         BIGINT NULL,               -- FK -> accounts_user(id), added below
    parent_id       BIGINT NULL REFERENCES organization_department(id) ON DELETE SET NULL,
    is_active       BOOLEAN NOT NULL DEFAULT TRUE,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX idx_department_parent ON organization_department(parent_id);

-- =============================================================================
-- accounts — custom User (employee profile)
-- =============================================================================

CREATE TABLE accounts_user (
    id                   BIGSERIAL PRIMARY KEY,
    password             VARCHAR(128) NOT NULL,
    last_login           TIMESTAMPTZ NULL,
    is_superuser         BOOLEAN NOT NULL DEFAULT FALSE,
    username             VARCHAR(150) NOT NULL UNIQUE,
    first_name           VARCHAR(150) NOT NULL DEFAULT '',
    last_name            VARCHAR(150) NOT NULL DEFAULT '',
    is_staff             BOOLEAN NOT NULL DEFAULT FALSE,
    is_active            BOOLEAN NOT NULL DEFAULT TRUE,
    date_joined          TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    -- AssetFlow-specific fields
    employee_id          VARCHAR(20) NOT NULL UNIQUE,
    email                VARCHAR(254) NOT NULL UNIQUE,
    role                 VARCHAR(20) NOT NULL DEFAULT 'employee'
                         CHECK (role IN ('admin', 'manager', 'employee')),
    department_id        BIGINT NULL REFERENCES organization_department(id) ON DELETE SET NULL,
    designation          VARCHAR(100) NOT NULL DEFAULT '',
    phone                VARCHAR(20) NOT NULL DEFAULT '',
    avatar               VARCHAR(100) NULL,          -- stored file path (ImageField)
    is_active_employee   BOOLEAN NOT NULL DEFAULT TRUE,
    date_joined_org      DATE NULL
);
CREATE INDEX idx_user_department ON accounts_user(department_id);
CREATE INDEX idx_user_role ON accounts_user(role);

-- Now that accounts_user exists, wire up organization_department.head_id
ALTER TABLE organization_department
    ADD CONSTRAINT fk_department_head
    FOREIGN KEY (head_id) REFERENCES accounts_user(id) ON DELETE SET NULL;
CREATE INDEX idx_department_head ON organization_department(head_id);

-- Django's built-in auth group/permission M2M tables for the custom user model.
-- (auth_group / auth_permission themselves are created by django.contrib.auth.)
CREATE TABLE accounts_user_groups (
    id          BIGSERIAL PRIMARY KEY,
    user_id     BIGINT NOT NULL REFERENCES accounts_user(id) ON DELETE CASCADE,
    group_id    INTEGER NOT NULL,   -- REFERENCES auth_group(id)
    UNIQUE (user_id, group_id)
);

CREATE TABLE accounts_user_user_permissions (
    id             BIGSERIAL PRIMARY KEY,
    user_id        BIGINT NOT NULL REFERENCES accounts_user(id) ON DELETE CASCADE,
    permission_id  INTEGER NOT NULL,  -- REFERENCES auth_permission(id)
    UNIQUE (user_id, permission_id)
);

-- =============================================================================
-- assets — Asset directory, allocation history, usage events
-- =============================================================================

CREATE TABLE assets_asset (
    id                  BIGSERIAL PRIMARY KEY,
    tag                 VARCHAR(20) NOT NULL UNIQUE,
    name                VARCHAR(150) NOT NULL,
    category_id         BIGINT NOT NULL REFERENCES organization_category(id) ON DELETE RESTRICT,
    status              VARCHAR(20) NOT NULL DEFAULT 'available'
                        CHECK (status IN ('available', 'allocated', 'maintenance', 'retired')),
    department_id       BIGINT NULL REFERENCES organization_department(id) ON DELETE SET NULL,
    current_holder_id   BIGINT NULL REFERENCES accounts_user(id) ON DELETE SET NULL,
    location            VARCHAR(150) NOT NULL DEFAULT '',
    qr_code             VARCHAR(64) NOT NULL UNIQUE,
    purchase_date       DATE NULL,
    purchase_value      NUMERIC(12, 2) NULL,
    service_due_date    DATE NULL,
    notes               TEXT NOT NULL DEFAULT '',
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX idx_asset_category ON assets_asset(category_id);
CREATE INDEX idx_asset_department ON assets_asset(department_id);
CREATE INDEX idx_asset_holder ON assets_asset(current_holder_id);
CREATE INDEX idx_asset_status ON assets_asset(status);
CREATE INDEX idx_asset_created_at ON assets_asset(created_at);

CREATE TABLE assets_allocationhistory (
    id              BIGSERIAL PRIMARY KEY,
    asset_id        BIGINT NOT NULL REFERENCES assets_asset(id) ON DELETE CASCADE,
    employee_id     BIGINT NULL REFERENCES accounts_user(id) ON DELETE SET NULL,
    department_id   BIGINT NULL REFERENCES organization_department(id) ON DELETE SET NULL,
    action          VARCHAR(20) NOT NULL
                    CHECK (action IN ('allocated', 'returned', 'transferred')),
    condition       VARCHAR(50) NOT NULL DEFAULT '',
    notes           TEXT NOT NULL DEFAULT '',
    occurred_at     TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX idx_allochistory_asset ON assets_allocationhistory(asset_id);
CREATE INDEX idx_allochistory_occurred ON assets_allocationhistory(occurred_at);

CREATE TABLE assets_assetusageevent (
    id              BIGSERIAL PRIMARY KEY,
    asset_id        BIGINT NOT NULL REFERENCES assets_asset(id) ON DELETE CASCADE,
    source          VARCHAR(30) NOT NULL,   -- 'booking' | 'transfer' | 'maintenance'
    occurred_at     TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX idx_usageevent_asset ON assets_assetusageevent(asset_id);
CREATE INDEX idx_usageevent_occurred ON assets_assetusageevent(occurred_at);

-- =============================================================================
-- transfers — Allocation & transfer requests
-- =============================================================================

CREATE TABLE transfers_transferrequest (
    id                BIGSERIAL PRIMARY KEY,
    asset_id          BIGINT NOT NULL REFERENCES assets_asset(id) ON DELETE CASCADE,
    from_employee_id  BIGINT NULL REFERENCES accounts_user(id) ON DELETE SET NULL,
    to_employee_id    BIGINT NOT NULL REFERENCES accounts_user(id) ON DELETE CASCADE,
    reason            TEXT NOT NULL,
    status            VARCHAR(20) NOT NULL DEFAULT 'pending'
                      CHECK (status IN ('pending', 'approved', 'rejected')),
    requested_by_id   BIGINT NULL REFERENCES accounts_user(id) ON DELETE SET NULL,
    resolved_by_id    BIGINT NULL REFERENCES accounts_user(id) ON DELETE SET NULL,
    created_at        TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    resolved_at       TIMESTAMPTZ NULL,

    CONSTRAINT chk_transfer_not_self CHECK (from_employee_id IS DISTINCT FROM to_employee_id)
);
CREATE INDEX idx_transfer_asset ON transfers_transferrequest(asset_id);
CREATE INDEX idx_transfer_status ON transfers_transferrequest(status);
CREATE INDEX idx_transfer_to_employee ON transfers_transferrequest(to_employee_id);

-- =============================================================================
-- bookings — Bookable resources & the booking calendar
-- =============================================================================

CREATE TABLE bookings_bookableresource (
    id          BIGSERIAL PRIMARY KEY,
    name        VARCHAR(150) NOT NULL,
    location    VARCHAR(150) NOT NULL DEFAULT '',
    capacity    INTEGER NULL,
    asset_id    BIGINT NULL UNIQUE REFERENCES assets_asset(id) ON DELETE SET NULL,
    is_active   BOOLEAN NOT NULL DEFAULT TRUE
);

CREATE TABLE bookings_booking (
    id             BIGSERIAL PRIMARY KEY,
    resource_id    BIGINT NOT NULL REFERENCES bookings_bookableresource(id) ON DELETE CASCADE,
    booked_by_id   BIGINT NOT NULL REFERENCES accounts_user(id) ON DELETE CASCADE,
    start_time     TIMESTAMPTZ NOT NULL,
    end_time       TIMESTAMPTZ NOT NULL,
    purpose        VARCHAR(255) NOT NULL DEFAULT '',
    status         VARCHAR(20) NOT NULL DEFAULT 'confirmed'
                   CHECK (status IN ('confirmed', 'conflict', 'cancelled')),
    created_at     TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT chk_booking_time_order CHECK (start_time < end_time)
);
CREATE INDEX idx_booking_resource ON bookings_booking(resource_id);
CREATE INDEX idx_booking_status ON bookings_booking(status);
-- Speeds up the overlap check ("does this resource already have a
-- confirmed booking that overlaps [start_time, end_time)?").
CREATE INDEX idx_booking_resource_window ON bookings_booking(resource_id, start_time, end_time);

-- =============================================================================
-- maintenance — Kanban tickets + status change log
-- =============================================================================

CREATE TABLE maintenance_maintenanceticket (
    id              BIGSERIAL PRIMARY KEY,
    asset_id        BIGINT NOT NULL REFERENCES assets_asset(id) ON DELETE CASCADE,
    reported_by_id  BIGINT NULL REFERENCES accounts_user(id) ON DELETE SET NULL,
    technician_id   BIGINT NULL REFERENCES accounts_user(id) ON DELETE SET NULL,
    issue           VARCHAR(255) NOT NULL,
    notes           TEXT NOT NULL DEFAULT '',
    priority        VARCHAR(10) NOT NULL DEFAULT 'medium'
                    CHECK (priority IN ('low', 'medium', 'high')),
    status          VARCHAR(20) NOT NULL DEFAULT 'pending'
                    CHECK (status IN ('pending', 'approved', 'assigned', 'in_progress', 'resolved')),
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    resolved_at     TIMESTAMPTZ NULL
);
CREATE INDEX idx_maint_asset ON maintenance_maintenanceticket(asset_id);
CREATE INDEX idx_maint_status ON maintenance_maintenanceticket(status);
CREATE INDEX idx_maint_technician ON maintenance_maintenanceticket(technician_id);

CREATE TABLE maintenance_maintenancestatuslog (
    id             BIGSERIAL PRIMARY KEY,
    ticket_id      BIGINT NOT NULL REFERENCES maintenance_maintenanceticket(id) ON DELETE CASCADE,
    from_status    VARCHAR(20) NOT NULL DEFAULT '',
    to_status      VARCHAR(20) NOT NULL,
    changed_by_id  BIGINT NULL REFERENCES accounts_user(id) ON DELETE SET NULL,
    changed_at     TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX idx_maintlog_ticket ON maintenance_maintenancestatuslog(ticket_id);

-- =============================================================================
-- audits — Audit cycles + per-asset verification rows
-- =============================================================================

CREATE TABLE audits_auditcycle (
    id             BIGSERIAL PRIMARY KEY,
    name           VARCHAR(150) NOT NULL,
    department_id  BIGINT NULL REFERENCES organization_department(id) ON DELETE SET NULL,
    start_date     DATE NOT NULL,
    end_date       DATE NOT NULL,
    status         VARCHAR(10) NOT NULL DEFAULT 'open'
                   CHECK (status IN ('open', 'closed')),
    created_at     TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    closed_at      TIMESTAMPTZ NULL,

    CONSTRAINT chk_audit_date_order CHECK (start_date <= end_date)
);
CREATE INDEX idx_auditcycle_department ON audits_auditcycle(department_id);
CREATE INDEX idx_auditcycle_status ON audits_auditcycle(status);

-- ManyToMany: AuditCycle.auditors
CREATE TABLE audits_auditcycle_auditors (
    id             BIGSERIAL PRIMARY KEY,
    auditcycle_id  BIGINT NOT NULL REFERENCES audits_auditcycle(id) ON DELETE CASCADE,
    user_id        BIGINT NOT NULL REFERENCES accounts_user(id) ON DELETE CASCADE,
    UNIQUE (auditcycle_id, user_id)
);

CREATE TABLE audits_audititem (
    id                  BIGSERIAL PRIMARY KEY,
    cycle_id            BIGINT NOT NULL REFERENCES audits_auditcycle(id) ON DELETE CASCADE,
    asset_id            BIGINT NOT NULL REFERENCES assets_asset(id) ON DELETE CASCADE,
    expected_location   VARCHAR(150) NOT NULL DEFAULT '',
    verification        VARCHAR(10) NOT NULL DEFAULT 'pending'
                        CHECK (verification IN ('pending', 'verified', 'missing', 'damaged')),
    notes               TEXT NOT NULL DEFAULT '',
    verified_by_id      BIGINT NULL REFERENCES accounts_user(id) ON DELETE SET NULL,
    verified_at         TIMESTAMPTZ NULL,

    UNIQUE (cycle_id, asset_id)
);
CREATE INDEX idx_audititem_cycle ON audits_audititem(cycle_id);
CREATE INDEX idx_audititem_verification ON audits_audititem(verification);

-- =============================================================================
-- notifications — Activity log / notification feed
-- =============================================================================

CREATE TABLE notifications_notification (
    id               BIGSERIAL PRIMARY KEY,
    recipient_id     BIGINT NOT NULL REFERENCES accounts_user(id) ON DELETE CASCADE,
    category         VARCHAR(20) NOT NULL DEFAULT 'general'
                     CHECK (category IN ('alert', 'approval', 'booking', 'general')),
    message          VARCHAR(255) NOT NULL,
    is_read          BOOLEAN NOT NULL DEFAULT FALSE,
    created_at       TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    -- Generic FK to whatever triggered the notification (a TransferRequest,
    -- Booking, MaintenanceTicket, AuditCycle, ...). django_content_type is
    -- created by django.contrib.contenttypes; referenced here, not defined.
    content_type_id  INTEGER NULL,     -- REFERENCES django_content_type(id)
    object_id        INTEGER NULL
);
CREATE INDEX idx_notification_recipient ON notifications_notification(recipient_id);
CREATE INDEX idx_notification_recipient_unread ON notifications_notification(recipient_id, is_read);
CREATE INDEX idx_notification_category ON notifications_notification(category);
CREATE INDEX idx_notification_content_object ON notifications_notification(content_type_id, object_id);
