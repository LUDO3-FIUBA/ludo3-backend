-- Migration 0059_dept_admins + creation of admin users for the 18 existing departments.
-- Run this on the remote DB. Order matters: the migration block must run before the INSERTs.
-- Default password for all generated admins is "test123" (PBKDF2-SHA256 / 216,000 iterations).
--
-- Both transactions are idempotent — re-running the file will not error if rows
-- or columns already exist.

-- =====================================================================
-- 1) Apply migration 0059_dept_admins (idempotent)
-- =====================================================================
BEGIN;

ALTER TABLE "backend_staff"      ADD COLUMN IF NOT EXISTS "department_id" integer NULL;
ALTER TABLE "backend_commission" ADD COLUMN IF NOT EXISTS "department_id" integer NULL;

DO $$ BEGIN
  ALTER TABLE "backend_staff"
      ADD CONSTRAINT "backend_staff_department_id_fk"
      FOREIGN KEY ("department_id") REFERENCES "backend_department" ("id")
      ON DELETE SET NULL DEFERRABLE INITIALLY DEFERRED;
EXCEPTION WHEN duplicate_object THEN NULL;
END $$;

DO $$ BEGIN
  ALTER TABLE "backend_commission"
      ADD CONSTRAINT "backend_commission_department_id_fk"
      FOREIGN KEY ("department_id") REFERENCES "backend_department" ("id")
      ON DELETE SET NULL DEFERRABLE INITIALLY DEFERRED;
EXCEPTION WHEN duplicate_object THEN NULL;
END $$;

CREATE INDEX IF NOT EXISTS "backend_staff_department_id_idx"      ON "backend_staff"      ("department_id");
CREATE INDEX IF NOT EXISTS "backend_commission_department_id_idx" ON "backend_commission" ("department_id");

INSERT INTO "django_migrations" ("app", "name", "applied")
VALUES ('backend', '0059_dept_admins', NOW())
ON CONFLICT DO NOTHING;

COMMIT;


-- =====================================================================
-- 2) Create one admin user per existing department.
-- Password hash below = "test123" (PBKDF2-SHA256, 216k iterations).
-- DNI is 8-digit, sequential by ascending department id.
--   dept 3  -> DNI 00000001
--   dept 4  -> DNI 00000002
--   ...
--   dept 20 -> DNI 00000018
-- Includes github_url='' (column added by 0059_user_github_url on develop).
-- INSERTs use ON CONFLICT DO NOTHING on dni/email so re-runs are safe.
-- =====================================================================
BEGIN;

WITH new_user AS (
  INSERT INTO "backend_user" (password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined, is_student, is_teacher, dni, github_url, created_at, updated_at)
  VALUES ('pbkdf2_sha256$216000$oUpIgSbqO0Ht$rG5qd+B8TUcVywJA7PQ8scQ+UT154acNIAFoJFp8Lu4=', NULL, false, '', 'Admin', 'Agrimensura', 'admin.dept3@dept.fi.uba.ar', true, true, NOW(), false, false, '00000001', '', NOW(), NOW())
  ON CONFLICT (dni) DO NOTHING
  RETURNING id
)
INSERT INTO "backend_staff" (user_id, department_siu_id, department_id) SELECT id, 0, 3 FROM new_user
ON CONFLICT (user_id) DO NOTHING;

WITH new_user AS (
  INSERT INTO "backend_user" (password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined, is_student, is_teacher, dni, github_url, created_at, updated_at)
  VALUES ('pbkdf2_sha256$216000$oUpIgSbqO0Ht$rG5qd+B8TUcVywJA7PQ8scQ+UT154acNIAFoJFp8Lu4=', NULL, false, '', 'Admin', 'Computación', 'admin.dept4@dept.fi.uba.ar', true, true, NOW(), false, false, '00000002', '', NOW(), NOW())
  ON CONFLICT (dni) DO NOTHING
  RETURNING id
)
INSERT INTO "backend_staff" (user_id, department_siu_id, department_id) SELECT id, 0, 4 FROM new_user
ON CONFLICT (user_id) DO NOTHING;

WITH new_user AS (
  INSERT INTO "backend_user" (password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined, is_student, is_teacher, dni, github_url, created_at, updated_at)
  VALUES ('pbkdf2_sha256$216000$oUpIgSbqO0Ht$rG5qd+B8TUcVywJA7PQ8scQ+UT154acNIAFoJFp8Lu4=', NULL, false, '', 'Admin', 'Construcciones y Estructuras', 'admin.dept5@dept.fi.uba.ar', true, true, NOW(), false, false, '00000003', '', NOW(), NOW())
  ON CONFLICT (dni) DO NOTHING
  RETURNING id
)
INSERT INTO "backend_staff" (user_id, department_siu_id, department_id) SELECT id, 0, 5 FROM new_user
ON CONFLICT (user_id) DO NOTHING;

WITH new_user AS (
  INSERT INTO "backend_user" (password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined, is_student, is_teacher, dni, github_url, created_at, updated_at)
  VALUES ('pbkdf2_sha256$216000$oUpIgSbqO0Ht$rG5qd+B8TUcVywJA7PQ8scQ+UT154acNIAFoJFp8Lu4=', NULL, false, '', 'Admin', 'Electrónica', 'admin.dept6@dept.fi.uba.ar', true, true, NOW(), false, false, '00000004', '', NOW(), NOW())
  ON CONFLICT (dni) DO NOTHING
  RETURNING id
)
INSERT INTO "backend_staff" (user_id, department_siu_id, department_id) SELECT id, 0, 6 FROM new_user
ON CONFLICT (user_id) DO NOTHING;

WITH new_user AS (
  INSERT INTO "backend_user" (password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined, is_student, is_teacher, dni, github_url, created_at, updated_at)
  VALUES ('pbkdf2_sha256$216000$oUpIgSbqO0Ht$rG5qd+B8TUcVywJA7PQ8scQ+UT154acNIAFoJFp8Lu4=', NULL, false, '', 'Admin', 'Energía', 'admin.dept7@dept.fi.uba.ar', true, true, NOW(), false, false, '00000005', '', NOW(), NOW())
  ON CONFLICT (dni) DO NOTHING
  RETURNING id
)
INSERT INTO "backend_staff" (user_id, department_siu_id, department_id) SELECT id, 0, 7 FROM new_user
ON CONFLICT (user_id) DO NOTHING;

WITH new_user AS (
  INSERT INTO "backend_user" (password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined, is_student, is_teacher, dni, github_url, created_at, updated_at)
  VALUES ('pbkdf2_sha256$216000$oUpIgSbqO0Ht$rG5qd+B8TUcVywJA7PQ8scQ+UT154acNIAFoJFp8Lu4=', NULL, false, '', 'Admin', 'Estabilidad', 'admin.dept8@dept.fi.uba.ar', true, true, NOW(), false, false, '00000006', '', NOW(), NOW())
  ON CONFLICT (dni) DO NOTHING
  RETURNING id
)
INSERT INTO "backend_staff" (user_id, department_siu_id, department_id) SELECT id, 0, 8 FROM new_user
ON CONFLICT (user_id) DO NOTHING;

WITH new_user AS (
  INSERT INTO "backend_user" (password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined, is_student, is_teacher, dni, github_url, created_at, updated_at)
  VALUES ('pbkdf2_sha256$216000$oUpIgSbqO0Ht$rG5qd+B8TUcVywJA7PQ8scQ+UT154acNIAFoJFp8Lu4=', NULL, false, '', 'Admin', 'Física', 'admin.dept9@dept.fi.uba.ar', true, true, NOW(), false, false, '00000007', '', NOW(), NOW())
  ON CONFLICT (dni) DO NOTHING
  RETURNING id
)
INSERT INTO "backend_staff" (user_id, department_siu_id, department_id) SELECT id, 0, 9 FROM new_user
ON CONFLICT (user_id) DO NOTHING;

WITH new_user AS (
  INSERT INTO "backend_user" (password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined, is_student, is_teacher, dni, github_url, created_at, updated_at)
  VALUES ('pbkdf2_sha256$216000$oUpIgSbqO0Ht$rG5qd+B8TUcVywJA7PQ8scQ+UT154acNIAFoJFp8Lu4=', NULL, false, '', 'Admin', 'Gestión', 'admin.dept10@dept.fi.uba.ar', true, true, NOW(), false, false, '00000008', '', NOW(), NOW())
  ON CONFLICT (dni) DO NOTHING
  RETURNING id
)
INSERT INTO "backend_staff" (user_id, department_siu_id, department_id) SELECT id, 0, 10 FROM new_user
ON CONFLICT (user_id) DO NOTHING;

WITH new_user AS (
  INSERT INTO "backend_user" (password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined, is_student, is_teacher, dni, github_url, created_at, updated_at)
  VALUES ('pbkdf2_sha256$216000$oUpIgSbqO0Ht$rG5qd+B8TUcVywJA7PQ8scQ+UT154acNIAFoJFp8Lu4=', NULL, false, '', 'Admin', 'Hidráulica', 'admin.dept11@dept.fi.uba.ar', true, true, NOW(), false, false, '00000009', '', NOW(), NOW())
  ON CONFLICT (dni) DO NOTHING
  RETURNING id
)
INSERT INTO "backend_staff" (user_id, department_siu_id, department_id) SELECT id, 0, 11 FROM new_user
ON CONFLICT (user_id) DO NOTHING;

WITH new_user AS (
  INSERT INTO "backend_user" (password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined, is_student, is_teacher, dni, github_url, created_at, updated_at)
  VALUES ('pbkdf2_sha256$216000$oUpIgSbqO0Ht$rG5qd+B8TUcVywJA7PQ8scQ+UT154acNIAFoJFp8Lu4=', NULL, false, '', 'Admin', 'Idiomas', 'admin.dept12@dept.fi.uba.ar', true, true, NOW(), false, false, '00000010', '', NOW(), NOW())
  ON CONFLICT (dni) DO NOTHING
  RETURNING id
)
INSERT INTO "backend_staff" (user_id, department_siu_id, department_id) SELECT id, 0, 12 FROM new_user
ON CONFLICT (user_id) DO NOTHING;

WITH new_user AS (
  INSERT INTO "backend_user" (password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined, is_student, is_teacher, dni, github_url, created_at, updated_at)
  VALUES ('pbkdf2_sha256$216000$oUpIgSbqO0Ht$rG5qd+B8TUcVywJA7PQ8scQ+UT154acNIAFoJFp8Lu4=', NULL, false, '', 'Admin', 'Ingeniería Mecánica', 'admin.dept13@dept.fi.uba.ar', true, true, NOW(), false, false, '00000011', '', NOW(), NOW())
  ON CONFLICT (dni) DO NOTHING
  RETURNING id
)
INSERT INTO "backend_staff" (user_id, department_siu_id, department_id) SELECT id, 0, 13 FROM new_user
ON CONFLICT (user_id) DO NOTHING;

WITH new_user AS (
  INSERT INTO "backend_user" (password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined, is_student, is_teacher, dni, github_url, created_at, updated_at)
  VALUES ('pbkdf2_sha256$216000$oUpIgSbqO0Ht$rG5qd+B8TUcVywJA7PQ8scQ+UT154acNIAFoJFp8Lu4=', NULL, false, '', 'Admin', 'Ingeniería Naval', 'admin.dept14@dept.fi.uba.ar', true, true, NOW(), false, false, '00000012', '', NOW(), NOW())
  ON CONFLICT (dni) DO NOTHING
  RETURNING id
)
INSERT INTO "backend_staff" (user_id, department_siu_id, department_id) SELECT id, 0, 14 FROM new_user
ON CONFLICT (user_id) DO NOTHING;

WITH new_user AS (
  INSERT INTO "backend_user" (password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined, is_student, is_teacher, dni, github_url, created_at, updated_at)
  VALUES ('pbkdf2_sha256$216000$oUpIgSbqO0Ht$rG5qd+B8TUcVywJA7PQ8scQ+UT154acNIAFoJFp8Lu4=', NULL, false, '', 'Admin', 'Ingeniería Química', 'admin.dept15@dept.fi.uba.ar', true, true, NOW(), false, false, '00000013', '', NOW(), NOW())
  ON CONFLICT (dni) DO NOTHING
  RETURNING id
)
INSERT INTO "backend_staff" (user_id, department_siu_id, department_id) SELECT id, 0, 15 FROM new_user
ON CONFLICT (user_id) DO NOTHING;

WITH new_user AS (
  INSERT INTO "backend_user" (password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined, is_student, is_teacher, dni, github_url, created_at, updated_at)
  VALUES ('pbkdf2_sha256$216000$oUpIgSbqO0Ht$rG5qd+B8TUcVywJA7PQ8scQ+UT154acNIAFoJFp8Lu4=', NULL, false, '', 'Admin', 'Matemática', 'admin.dept16@dept.fi.uba.ar', true, true, NOW(), false, false, '00000014', '', NOW(), NOW())
  ON CONFLICT (dni) DO NOTHING
  RETURNING id
)
INSERT INTO "backend_staff" (user_id, department_siu_id, department_id) SELECT id, 0, 16 FROM new_user
ON CONFLICT (user_id) DO NOTHING;

WITH new_user AS (
  INSERT INTO "backend_user" (password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined, is_student, is_teacher, dni, github_url, created_at, updated_at)
  VALUES ('pbkdf2_sha256$216000$oUpIgSbqO0Ht$rG5qd+B8TUcVywJA7PQ8scQ+UT154acNIAFoJFp8Lu4=', NULL, false, '', 'Admin', 'Química', 'admin.dept17@dept.fi.uba.ar', true, true, NOW(), false, false, '00000015', '', NOW(), NOW())
  ON CONFLICT (dni) DO NOTHING
  RETURNING id
)
INSERT INTO "backend_staff" (user_id, department_siu_id, department_id) SELECT id, 0, 17 FROM new_user
ON CONFLICT (user_id) DO NOTHING;

WITH new_user AS (
  INSERT INTO "backend_user" (password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined, is_student, is_teacher, dni, github_url, created_at, updated_at)
  VALUES ('pbkdf2_sha256$216000$oUpIgSbqO0Ht$rG5qd+B8TUcVywJA7PQ8scQ+UT154acNIAFoJFp8Lu4=', NULL, false, '', 'Admin', 'Seguridad del Trabajo y Ambiente', 'admin.dept18@dept.fi.uba.ar', true, true, NOW(), false, false, '00000016', '', NOW(), NOW())
  ON CONFLICT (dni) DO NOTHING
  RETURNING id
)
INSERT INTO "backend_staff" (user_id, department_siu_id, department_id) SELECT id, 0, 18 FROM new_user
ON CONFLICT (user_id) DO NOTHING;

WITH new_user AS (
  INSERT INTO "backend_user" (password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined, is_student, is_teacher, dni, github_url, created_at, updated_at)
  VALUES ('pbkdf2_sha256$216000$oUpIgSbqO0Ht$rG5qd+B8TUcVywJA7PQ8scQ+UT154acNIAFoJFp8Lu4=', NULL, false, '', 'Admin', 'Tecnología Industrial', 'admin.dept19@dept.fi.uba.ar', true, true, NOW(), false, false, '00000017', '', NOW(), NOW())
  ON CONFLICT (dni) DO NOTHING
  RETURNING id
)
INSERT INTO "backend_staff" (user_id, department_siu_id, department_id) SELECT id, 0, 19 FROM new_user
ON CONFLICT (user_id) DO NOTHING;

WITH new_user AS (
  INSERT INTO "backend_user" (password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined, is_student, is_teacher, dni, github_url, created_at, updated_at)
  VALUES ('pbkdf2_sha256$216000$oUpIgSbqO0Ht$rG5qd+B8TUcVywJA7PQ8scQ+UT154acNIAFoJFp8Lu4=', NULL, false, '', 'Admin', 'Transporte', 'admin.dept20@dept.fi.uba.ar', true, true, NOW(), false, false, '00000018', '', NOW(), NOW())
  ON CONFLICT (dni) DO NOTHING
  RETURNING id
)
INSERT INTO "backend_staff" (user_id, department_siu_id, department_id) SELECT id, 0, 20 FROM new_user
ON CONFLICT (user_id) DO NOTHING;

COMMIT;
