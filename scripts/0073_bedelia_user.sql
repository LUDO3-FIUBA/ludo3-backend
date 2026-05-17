-- Migration 0073_staff_is_bedelia + creation of the single global bedelía admin user.
-- Run on the remote DB. Password is "test123" (PBKDF2-SHA256 / 216k).
-- Both transactions are idempotent — safe to re-run.

-- =====================================================================
-- 1) Apply migration 0073_staff_is_bedelia
-- =====================================================================
BEGIN;

ALTER TABLE "backend_staff" ADD COLUMN IF NOT EXISTS "is_bedelia" boolean NOT NULL DEFAULT false;

INSERT INTO "django_migrations" ("app", "name", "applied")
VALUES ('backend', '0073_staff_is_bedelia', NOW())
ON CONFLICT DO NOTHING;

COMMIT;


-- =====================================================================
-- 2) Create the global bedelía user.
-- DNI 00000019 (next available after dept admins, which use 00000001–00000018).
-- Password hash below = "test123".
-- =====================================================================
BEGIN;

WITH new_user AS (
  INSERT INTO "backend_user" (password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined, is_student, is_teacher, dni, github_url, linkedin_url, created_at, updated_at)
  VALUES ('pbkdf2_sha256$216000$oUpIgSbqO0Ht$rG5qd+B8TUcVywJA7PQ8scQ+UT154acNIAFoJFp8Lu4=', NULL, false, '', 'Bedelía', 'FIUBA', 'bedelia@dept.fi.uba.ar', true, true, NOW(), false, false, '00000019', '', '', NOW(), NOW())
  ON CONFLICT (dni) DO NOTHING
  RETURNING id
)
INSERT INTO "backend_staff" (user_id, department_siu_id, department_id, is_bedelia)
SELECT id, 0, NULL, true FROM new_user
ON CONFLICT (user_id) DO NOTHING;

COMMIT;
