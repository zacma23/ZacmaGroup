-- ============================================================================
-- Migration: 20260823000006_payment_providers_and_transactions.sql
-- Description: Multi-Provider Payment Management Platform (Chapa, CBE, Telebirr,
--              Awash, Generic Banks), Transactions, Webhooks, Balances & Audit Logs.
-- ============================================================================

-- ============================================================================
-- Table: public.payment_providers
-- Configurable payment providers managed dynamically by administrators
-- ============================================================================
CREATE TABLE IF NOT EXISTS public.payment_providers (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id UUID NOT NULL REFERENCES public.tenants(id) ON DELETE CASCADE,
  provider_name TEXT NOT NULL,
  provider_code TEXT NOT NULL,
  provider_type TEXT NOT NULL CHECK (provider_type IN ('gateway', 'bank_transfer', 'mobile_money', 'custom')),
  is_active BOOLEAN NOT NULL DEFAULT true,
  is_default BOOLEAN NOT NULL DEFAULT false,
  priority INT NOT NULL DEFAULT 1,
  environment TEXT NOT NULL DEFAULT 'test' CHECK (environment IN ('test', 'live', 'sandbox')),
  currency TEXT NOT NULL DEFAULT 'ETB',
  supported_currencies TEXT[] DEFAULT ARRAY['ETB']::TEXT[],
  account_name TEXT,
  account_number TEXT,
  customer_payment_number TEXT,
  instructions TEXT,
  api_endpoint TEXT,
  callback_url TEXT,
  webhook_url TEXT,
  supports_balance_api BOOLEAN NOT NULL DEFAULT false,
  transaction_fee_percent NUMERIC(5, 2) DEFAULT 0.00,
  transaction_fee_fixed NUMERIC(10, 2) DEFAULT 0.00,
  metadata JSONB DEFAULT '{}'::jsonb,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  CONSTRAINT uq_payment_providers_code UNIQUE (tenant_id, provider_code)
);

CREATE INDEX IF NOT EXISTS idx_payment_providers_tenant ON public.payment_providers(tenant_id);
CREATE INDEX IF NOT EXISTS idx_payment_providers_active ON public.payment_providers(is_active);
CREATE INDEX IF NOT EXISTS idx_payment_providers_code ON public.payment_providers(provider_code);

-- ============================================================================
-- Table: public.payment_provider_credentials
-- Encrypted / secure server-side credentials (NEVER exposed to frontend)
-- ============================================================================
CREATE TABLE IF NOT EXISTS public.payment_provider_credentials (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id UUID NOT NULL REFERENCES public.tenants(id) ON DELETE CASCADE,
  provider_id UUID NOT NULL REFERENCES public.payment_providers(id) ON DELETE CASCADE,
  api_key TEXT,
  secret_key TEXT,
  merchant_id TEXT,
  webhook_secret TEXT,
  public_key TEXT,
  additional_config JSONB DEFAULT '{}'::jsonb,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  CONSTRAINT uq_payment_provider_creds UNIQUE (provider_id)
);

CREATE INDEX IF NOT EXISTS idx_payment_provider_creds_tenant ON public.payment_provider_credentials(tenant_id);

-- ============================================================================
-- Table: public.payment_transactions
-- Granular ledger of all payment requests, checkout sessions, and completions
-- ============================================================================
CREATE TABLE IF NOT EXISTS public.payment_transactions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id UUID NOT NULL REFERENCES public.tenants(id) ON DELETE CASCADE,
  public_reference TEXT NOT NULL,
  customer_id UUID REFERENCES public.crm_contacts(id) ON DELETE SET NULL,
  customer_name TEXT NOT NULL,
  customer_email TEXT,
  customer_phone TEXT,
  provider_id UUID REFERENCES public.payment_providers(id) ON DELETE SET NULL,
  provider_code TEXT NOT NULL,
  payment_method TEXT NOT NULL,
  amount NUMERIC(12, 2) NOT NULL,
  fee NUMERIC(10, 2) DEFAULT 0.00,
  net_amount NUMERIC(12, 2) NOT NULL,
  currency TEXT NOT NULL DEFAULT 'ETB',
  status TEXT NOT NULL DEFAULT 'pending' CHECK (
    status IN ('pending', 'initiated', 'processing', 'successful', 'failed', 'cancelled', 'expired', 'refunded', 'partially_refunded')
  ),
  payment_purpose TEXT NOT NULL DEFAULT 'Service Fee',
  description TEXT,
  invoice_id UUID REFERENCES public.invoices(id) ON DELETE SET NULL,
  provider_transaction_id TEXT,
  provider_reference TEXT,
  checkout_url TEXT,
  callback_status TEXT,
  verification_status TEXT DEFAULT 'unverified',
  error_message TEXT,
  metadata JSONB DEFAULT '{}'::jsonb,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  completed_at TIMESTAMPTZ,
  CONSTRAINT uq_payment_tx_public_ref UNIQUE (tenant_id, public_reference)
);

CREATE INDEX IF NOT EXISTS idx_payment_tx_tenant ON public.payment_transactions(tenant_id);
CREATE INDEX IF NOT EXISTS idx_payment_tx_ref ON public.payment_transactions(public_reference);
CREATE INDEX IF NOT EXISTS idx_payment_tx_status ON public.payment_transactions(status);
CREATE INDEX IF NOT EXISTS idx_payment_tx_provider ON public.payment_transactions(provider_code);
CREATE INDEX IF NOT EXISTS idx_payment_tx_invoice ON public.payment_transactions(invoice_id);

-- ============================================================================
-- Table: public.payment_webhooks
-- Secure webhook log with signature validation & idempotency tracking
-- ============================================================================
CREATE TABLE IF NOT EXISTS public.payment_webhooks (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id UUID NOT NULL REFERENCES public.tenants(id) ON DELETE CASCADE,
  provider_code TEXT NOT NULL,
  event_type TEXT NOT NULL,
  transaction_reference TEXT,
  payload JSONB NOT NULL,
  signature TEXT,
  is_verified BOOLEAN NOT NULL DEFAULT false,
  is_processed BOOLEAN NOT NULL DEFAULT false,
  idempotency_key TEXT,
  error_message TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  CONSTRAINT uq_payment_webhook_idempotency UNIQUE (tenant_id, provider_code, idempotency_key)
);

CREATE INDEX IF NOT EXISTS idx_payment_webhooks_tenant ON public.payment_webhooks(tenant_id);
CREATE INDEX IF NOT EXISTS idx_payment_webhooks_tx_ref ON public.payment_webhooks(transaction_reference);

-- ============================================================================
-- Table: public.payment_balances
-- Tracks provider-reported balance vs internal platform ledger balance
-- ============================================================================
CREATE TABLE IF NOT EXISTS public.payment_balances (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id UUID NOT NULL REFERENCES public.tenants(id) ON DELETE CASCADE,
  provider_id UUID NOT NULL REFERENCES public.payment_providers(id) ON DELETE CASCADE,
  provider_reported_balance NUMERIC(14, 2) DEFAULT NULL,
  internal_platform_balance NUMERIC(14, 2) NOT NULL DEFAULT 0.00,
  pending_balance NUMERIC(14, 2) NOT NULL DEFAULT 0.00,
  total_received NUMERIC(14, 2) NOT NULL DEFAULT 0.00,
  total_transferred NUMERIC(14, 2) NOT NULL DEFAULT 0.00,
  total_refunded NUMERIC(14, 2) NOT NULL DEFAULT 0.00,
  currency TEXT NOT NULL DEFAULT 'ETB',
  balance_available_from_api BOOLEAN NOT NULL DEFAULT false,
  last_synced_at TIMESTAMPTZ,
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  CONSTRAINT uq_payment_balances_provider UNIQUE (provider_id)
);

CREATE INDEX IF NOT EXISTS idx_payment_balances_tenant ON public.payment_balances(tenant_id);

-- ============================================================================
-- Table: public.payment_logs
-- Immutable audit log for provider configs, verifications, refunds & security events
-- ============================================================================
CREATE TABLE IF NOT EXISTS public.payment_logs (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id UUID NOT NULL REFERENCES public.tenants(id) ON DELETE CASCADE,
  actor TEXT NOT NULL DEFAULT 'system',
  action TEXT NOT NULL,
  resource_type TEXT NOT NULL,
  resource_id TEXT,
  details JSONB DEFAULT '{}'::jsonb,
  ip_address TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_payment_logs_tenant ON public.payment_logs(tenant_id);
CREATE INDEX IF NOT EXISTS idx_payment_logs_action ON public.payment_logs(action);
CREATE INDEX IF NOT EXISTS idx_payment_logs_created_at ON public.payment_logs(created_at);
