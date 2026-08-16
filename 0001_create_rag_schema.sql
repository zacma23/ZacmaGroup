-- PROPOSAL: 0001_create_rag_schema.sql (placed at repo root)
-- WARNING: Do NOT run in production until architecture approval and review.

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS pgcrypto;
CREATE EXTENSION IF NOT EXISTS vector;

-- ============================
-- Schema creation (logical grouping)
-- ============================
CREATE SCHEMA IF NOT EXISTS public;
CREATE SCHEMA IF NOT EXISTS rag;
CREATE SCHEMA IF NOT EXISTS audit;
CREATE SCHEMA IF NOT EXISTS ai;
CREATE SCHEMA IF NOT EXISTS admin;

-- ============================
-- tenants
-- ============================
CREATE TABLE IF NOT EXISTS public.tenants (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name TEXT NOT NULL,
  slug TEXT UNIQUE NOT NULL,
  plan TEXT NOT NULL DEFAULT 'free',
  status TEXT NOT NULL DEFAULT 'active',
  metadata JSONB DEFAULT '{}',
  created_at timestamptz NOT NULL DEFAULT now(),
  created_by UUID,
  updated_at timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_tenants_slug ON public.tenants(slug);

-- ============================
-- users
-- ============================
CREATE TABLE IF NOT EXISTS public.users (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id UUID NOT NULL REFERENCES public.tenants(id) ON DELETE CASCADE,
  email TEXT NOT NULL,
  email_verified BOOLEAN NOT NULL DEFAULT FALSE,
  full_name TEXT,
  role TEXT NOT NULL DEFAULT 'user',
  status TEXT NOT NULL DEFAULT 'active',
  metadata JSONB DEFAULT '{}',
  created_at timestamptz NOT NULL DEFAULT now(),
  created_by UUID,
  updated_at timestamptz NOT NULL DEFAULT now()
);
CREATE UNIQUE INDEX IF NOT EXISTS idx_users_tenant_email ON public.users(tenant_id, email);

-- ============================
-- documents
-- ============================
CREATE TABLE IF NOT EXISTS rag.documents (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id UUID NOT NULL REFERENCES public.tenants(id) ON DELETE CASCADE,
  source_uri TEXT,
  title TEXT,
  description TEXT,
  content_type TEXT,
  content_size_bytes BIGINT,
  language TEXT,
  checksum TEXT,
  metadata JSONB NOT NULL DEFAULT '{}',
  status TEXT NOT NULL DEFAULT 'quarantine',
  ingestion_job_id UUID,
  created_at timestamptz NOT NULL DEFAULT now(),
  created_by UUID,
  updated_at timestamptz NOT NULL DEFAULT now(),
  deleted_at timestamptz,
  version INT NOT NULL DEFAULT 1
);
CREATE INDEX IF NOT EXISTS idx_documents_tenant_created_at ON rag.documents(tenant_id, created_at);
CREATE INDEX IF NOT EXISTS idx_documents_checksum ON rag.documents(tenant_id, checksum);
CREATE INDEX IF NOT EXISTS idx_documents_metadata_gin ON rag.documents USING gin (metadata jsonb_path_ops);

-- ============================
-- document_chunks
-- ============================
CREATE TABLE IF NOT EXISTS rag.document_chunks (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  document_id UUID NOT NULL REFERENCES rag.documents(id) ON DELETE CASCADE,
  tenant_id UUID NOT NULL REFERENCES public.tenants(id) ON DELETE CASCADE,
  chunk_order INT NOT NULL,
  chunk_text TEXT NOT NULL,
  chunk_tokens INT NOT NULL,
  chunk_hash TEXT NOT NULL,
  metadata JSONB NOT NULL DEFAULT '{}',
  created_at timestamptz NOT NULL DEFAULT now(),
  CONSTRAINT uq_chunks_document_order UNIQUE (document_id, chunk_order)
);
CREATE INDEX IF NOT EXISTS idx_chunks_tenant_chunk_hash ON rag.document_chunks(tenant_id, chunk_hash);

-- ============================
-- embeddings
-- ============================
-- Note: adjust 'vector' dimension in application before inserting
CREATE TABLE IF NOT EXISTS rag.embeddings (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  chunk_id UUID NOT NULL REFERENCES rag.document_chunks(id) ON DELETE CASCADE,
  document_id UUID NOT NULL REFERENCES rag.documents(id) ON DELETE CASCADE,
  tenant_id UUID NOT NULL REFERENCES public.tenants(id) ON DELETE CASCADE,
  model_name TEXT NOT NULL,
  model_version TEXT,
  embedding vector NOT NULL,
  embedding_norm DOUBLE PRECISION,
  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_embeddings_tenant_doc ON rag.embeddings(tenant_id, document_id);
-- Vector index: choose HNSW or ivfflat depending on pgvector version and scale
-- Example ivfflat (requires setting lists tuned to dataset size):
-- CREATE INDEX idx_embeddings_embedding_ivfflat ON rag.embeddings USING ivfflat (embedding vector_l2_ops) WITH (lists = 128);
-- Example HNSW (if supported):
-- CREATE INDEX idx_embeddings_embedding_hnsw ON rag.embeddings USING hnsw (embedding);

-- ============================
-- ingestion_jobs
-- ============================
CREATE TABLE IF NOT EXISTS rag.ingestion_jobs (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id UUID NOT NULL REFERENCES public.tenants(id),
  source_uri TEXT,
  uploader_id UUID,
  status TEXT NOT NULL DEFAULT 'pending',
  reason TEXT,
  started_at timestamptz,
  completed_at timestamptz,
  created_at timestamptz NOT NULL DEFAULT now(),
  metadata JSONB DEFAULT '{}'
);
CREATE INDEX IF NOT EXISTS idx_ingestion_jobs_tenant_status ON rag.ingestion_jobs(tenant_id, status);

-- ============================
-- audit.ingestion_audit
-- ============================
CREATE TABLE IF NOT EXISTS audit.ingestion_audit (
  id BIGSERIAL PRIMARY KEY,
  ingestion_job_id UUID NOT NULL REFERENCES rag.ingestion_jobs(id),
  event_time timestamptz NOT NULL DEFAULT now(),
  event_type TEXT NOT NULL,
  actor UUID,
  details JSONB
);
CREATE INDEX IF NOT EXISTS idx_ingest_audit_job ON audit.ingestion_audit(ingestion_job_id);

-- ============================
-- ai.retrieval_logs
-- ============================
CREATE TABLE IF NOT EXISTS ai.retrieval_logs (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id UUID NOT NULL REFERENCES public.tenants(id),
  user_id UUID,
  query_text TEXT,
  retrieved_topk INT,
  retrieval_time_ms INT,
  retrieval_result JSONB,
  model_name TEXT,
  cost_estimate NUMERIC,
  created_at timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_retrieval_tenant_created_at ON ai.retrieval_logs(tenant_id, created_at);

-- ============================
-- admin.access_policies
-- ============================
CREATE TABLE IF NOT EXISTS admin.access_policies (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id UUID NOT NULL REFERENCES public.tenants(id),
  resource_type TEXT NOT NULL,
  resource_id UUID,
  principal_type TEXT NOT NULL,
  principal_id UUID,
  permission TEXT NOT NULL,
  created_at timestamptz DEFAULT now()
);

-- ============================
-- RLS policy examples (must be enabled/managed by DB admin via application)
-- Example only: application sets session var 'zacma.tenant_id' to enforce RLS
--
-- ALTER TABLE rag.documents ENABLE ROW LEVEL SECURITY;
-- CREATE POLICY tenant_isolation_documents ON rag.documents
--   USING (tenant_id = current_setting('zacma.tenant_id')::uuid)
--   WITH CHECK (tenant_id = current_setting('zacma.tenant_id')::uuid);

-- ============================
-- End of PROPOSAL migration
