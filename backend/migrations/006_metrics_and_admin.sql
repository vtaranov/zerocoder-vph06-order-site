BEGIN;
-- Upgrade VPh05 without deleting applications or the two existing metric rows.
ALTER TABLE behavior_metrics DROP CONSTRAINT behavior_metrics_pkey;
ALTER TABLE behavior_metrics ALTER COLUMN application_id DROP NOT NULL;
ALTER TABLE behavior_metrics ADD COLUMN id SERIAL PRIMARY KEY;
ALTER TABLE behavior_metrics ADD COLUMN session_id VARCHAR(64);
UPDATE behavior_metrics SET session_id = 'legacy-' || id::text;
ALTER TABLE behavior_metrics ALTER COLUMN session_id SET NOT NULL;
ALTER TABLE behavior_metrics ADD CONSTRAINT behavior_metrics_session_id_key UNIQUE(session_id);
ALTER TABLE behavior_metrics ADD COLUMN layout VARCHAR(16) NOT NULL DEFAULT 'legacy';
ALTER TABLE behavior_metrics ADD COLUMN sequence INTEGER NOT NULL DEFAULT 0;
ALTER TABLE behavior_metrics ADD COLUMN started_at TIMESTAMPTZ NOT NULL DEFAULT now();
ALTER TABLE behavior_metrics ADD COLUMN updated_at TIMESTAMPTZ NOT NULL DEFAULT now();
UPDATE behavior_metrics b SET started_at = a.created_at, updated_at = a.created_at FROM applications a WHERE a.id = b.application_id;
CREATE TABLE admins (id INTEGER PRIMARY KEY CHECK(id=1), username VARCHAR(80) UNIQUE NOT NULL,
 password_hash VARCHAR(300) NOT NULL, created_at TIMESTAMPTZ NOT NULL DEFAULT now());
COMMIT;
