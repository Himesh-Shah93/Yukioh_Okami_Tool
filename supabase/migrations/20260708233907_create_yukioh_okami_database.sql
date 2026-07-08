/*
# Yukioh Okami Tool Database — Full Schema

## Purpose
Persists license key verification records, discovered encryption keys (SM4/XOR),
PAK unpack/repack operation logs, and tool session activity for the
Yukioh Okami PAK/LUA modding toolkit. This is a single-tenant CLI tool with
no Supabase sign-in screen — the anon-key client reads and writes its own data.

## 1. New Tables

### `license_verifications`
Stores every license key verification attempt (success or failure).
- `id` (uuid, PK) — auto-generated
- `user_key` (text) — the license key string entered by the user
- `hwid` (text) — hardware ID sent with the verification
- `status` (boolean) — true if verification succeeded, false otherwise
- `modname` (text) — mod name returned by the panel on success
- `credit` (text) — credit/balance returned by the panel
- `expiry` (timestamptz) — license expiry date returned by the panel
- `token` (text) — session token returned by the panel
- `failure_reason` (text) — reason string on failure (null on success)
- `verified_at` (timestamptz) — when the verification was attempted

### `found_keys`
Stores encryption keys discovered by the SM4/UE4/GFP key finder scripts.
- `id` (uuid, PK) — auto-generated
- `key_value` (text, not null) — the discovered key (hex or raw string)
- `key_type` (text, not null) — 'SM4', 'XOR', 'GFP', or other identifier
- `source_file` (text) — path/name of the binary the key was extracted from
- `key_offset` (bigint) — byte offset where the key was found (null if N/A)
- `confidence` (real) — confidence score 0.0–1.0
- `description` (text) — additional context (e.g. "known key", "pattern match")
- `finder_tool` (text) — which script found it
- `found_at` (timestamptz) — when the key was discovered

### `pak_operations`
Logs every PAK unpack/repack/decompile/compile operation.
- `id` (uuid, PK) — auto-generated
- `operation` (text, not null) — 'unpack', 'repack', 'decompile', 'compile', 'extract_keys'
- `input_path` (text) — source PAK file or folder path
- `output_path` (text) — output path
- `pak_stem` (text) — stem name of the PAK file being processed
- `file_count` (integer) — number of files processed
- `status` (text, not null) — 'success', 'failed', 'partial'
- `error_message` (text) — error details on failure (null on success)
- `duration_ms` (integer) — operation duration in milliseconds
- `operation_at` (timestamptz) — when the operation was executed

### `tool_sessions`
Records each tool launch session.
- `id` (uuid, PK) — auto-generated
- `hwid` (text) — hardware ID of the machine
- `tool_name` (text, not null) — tool name
- `version` (text) — tool version if available
- `authenticated` (boolean) — true if license auth succeeded
- `started_at` (timestamptz) — session start time
- `ended_at` (timestamptz) — session end time (null if still active or crashed)

## 2. Indexes
- `idx_license_hwid` on `license_verifications(hwid)`
- `idx_found_keys_type` on `found_keys(key_type)`
- `idx_found_keys_source` on `found_keys(source_file)`
- `idx_pak_ops_stem` on `pak_operations(pak_stem)`
- `idx_pak_ops_type` on `pak_operations(operation)`
- `idx_sessions_hwid` on `tool_sessions(hwid)`

## 3. Security (RLS)
- RLS enabled on all 4 tables.
- All policies use `TO anon, authenticated` (single-tenant CLI tool, no Supabase auth).
- 4 CRUD policies per table (select, insert, update, delete).

## 4. Important Notes
- No `user_id` columns or `auth.users` foreign keys — no Supabase auth.
- `offset` is a reserved Postgres keyword, so the column is named `key_offset`.
- All timestamps use `timestamptz` with `DEFAULT now()`.
- Idempotent: `IF NOT EXISTS` on tables/indexes, drop-before-create on policies.
*/

-- ============================================================
-- Table: license_verifications
-- ============================================================
CREATE TABLE IF NOT EXISTS license_verifications (
    id             uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    user_key       text,
    hwid           text,
    status         boolean NOT NULL DEFAULT false,
    modname        text,
    credit         text,
    expiry         timestamptz,
    token          text,
    failure_reason text,
    verified_at    timestamptz NOT NULL DEFAULT now()
);

ALTER TABLE license_verifications ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "select_license_verifications" ON license_verifications;
CREATE POLICY "select_license_verifications" ON license_verifications
    FOR SELECT TO anon, authenticated USING (true);

DROP POLICY IF EXISTS "insert_license_verifications" ON license_verifications;
CREATE POLICY "insert_license_verifications" ON license_verifications
    FOR INSERT TO anon, authenticated WITH CHECK (true);

DROP POLICY IF EXISTS "update_license_verifications" ON license_verifications;
CREATE POLICY "update_license_verifications" ON license_verifications
    FOR UPDATE TO anon, authenticated USING (true) WITH CHECK (true);

DROP POLICY IF EXISTS "delete_license_verifications" ON license_verifications;
CREATE POLICY "delete_license_verifications" ON license_verifications
    FOR DELETE TO anon, authenticated USING (true);

-- ============================================================
-- Table: found_keys
-- ============================================================
CREATE TABLE IF NOT EXISTS found_keys (
    id            uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    key_value     text NOT NULL,
    key_type      text NOT NULL,
    source_file   text,
    key_offset    bigint,
    confidence    real DEFAULT 0.0,
    description   text,
    finder_tool   text,
    found_at      timestamptz NOT NULL DEFAULT now()
);

ALTER TABLE found_keys ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "select_found_keys" ON found_keys;
CREATE POLICY "select_found_keys" ON found_keys
    FOR SELECT TO anon, authenticated USING (true);

DROP POLICY IF EXISTS "insert_found_keys" ON found_keys;
CREATE POLICY "insert_found_keys" ON found_keys
    FOR INSERT TO anon, authenticated WITH CHECK (true);

DROP POLICY IF EXISTS "update_found_keys" ON found_keys;
CREATE POLICY "update_found_keys" ON found_keys
    FOR UPDATE TO anon, authenticated USING (true) WITH CHECK (true);

DROP POLICY IF EXISTS "delete_found_keys" ON found_keys;
CREATE POLICY "delete_found_keys" ON found_keys
    FOR DELETE TO anon, authenticated USING (true);

-- ============================================================
-- Table: pak_operations
-- ============================================================
CREATE TABLE IF NOT EXISTS pak_operations (
    id            uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    operation     text NOT NULL,
    input_path    text,
    output_path   text,
    pak_stem      text,
    file_count    integer DEFAULT 0,
    status        text NOT NULL DEFAULT 'success',
    error_message text,
    duration_ms   integer,
    operation_at  timestamptz NOT NULL DEFAULT now()
);

ALTER TABLE pak_operations ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "select_pak_operations" ON pak_operations;
CREATE POLICY "select_pak_operations" ON pak_operations
    FOR SELECT TO anon, authenticated USING (true);

DROP POLICY IF EXISTS "insert_pak_operations" ON pak_operations;
CREATE POLICY "insert_pak_operations" ON pak_operations
    FOR INSERT TO anon, authenticated WITH CHECK (true);

DROP POLICY IF EXISTS "update_pak_operations" ON pak_operations;
CREATE POLICY "update_pak_operations" ON pak_operations
    FOR UPDATE TO anon, authenticated USING (true) WITH CHECK (true);

DROP POLICY IF EXISTS "delete_pak_operations" ON pak_operations;
CREATE POLICY "delete_pak_operations" ON pak_operations
    FOR DELETE TO anon, authenticated USING (true);

-- ============================================================
-- Table: tool_sessions
-- ============================================================
CREATE TABLE IF NOT EXISTS tool_sessions (
    id            uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    hwid          text,
    tool_name     text NOT NULL,
    version       text,
    authenticated boolean DEFAULT false,
    started_at    timestamptz NOT NULL DEFAULT now(),
    ended_at      timestamptz
);

ALTER TABLE tool_sessions ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "select_tool_sessions" ON tool_sessions;
CREATE POLICY "select_tool_sessions" ON tool_sessions
    FOR SELECT TO anon, authenticated USING (true);

DROP POLICY IF EXISTS "insert_tool_sessions" ON tool_sessions;
CREATE POLICY "insert_tool_sessions" ON tool_sessions
    FOR INSERT TO anon, authenticated WITH CHECK (true);

DROP POLICY IF EXISTS "update_tool_sessions" ON tool_sessions;
CREATE POLICY "update_tool_sessions" ON tool_sessions
    FOR UPDATE TO anon, authenticated USING (true) WITH CHECK (true);

DROP POLICY IF EXISTS "delete_tool_sessions" ON tool_sessions;
CREATE POLICY "delete_tool_sessions" ON tool_sessions
    FOR DELETE TO anon, authenticated USING (true);

-- ============================================================
-- Indexes
-- ============================================================
CREATE INDEX IF NOT EXISTS idx_license_hwid      ON license_verifications(hwid);
CREATE INDEX IF NOT EXISTS idx_found_keys_type    ON found_keys(key_type);
CREATE INDEX IF NOT EXISTS idx_found_keys_source  ON found_keys(source_file);
CREATE INDEX IF NOT EXISTS idx_pak_ops_stem       ON pak_operations(pak_stem);
CREATE INDEX IF NOT EXISTS idx_pak_ops_type       ON pak_operations(operation);
CREATE INDEX IF NOT EXISTS idx_sessions_hwid      ON tool_sessions(hwid);
