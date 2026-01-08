CREATE SCHEMA IF NOT EXISTS staging;
CREATE SCHEMA IF NOT EXISTS mart;
CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS staging.sales_raw (
    id BIGSERIAL PRIMARY KEY,
    pharma_id TEXT NOT NULL,
    extracted_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    payload JSONB NOT NULL
);

CREATE TABLE IF NOT EXISTS staging.products_raw (
    id BIGSERIAL PRIMARY KEY,
    pharma_id TEXT NOT NULL,
    extracted_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    payload JSONB NOT NULL
);

CREATE TABLE IF NOT EXISTS staging.stock_raw (
    id BIGSERIAL PRIMARY KEY,
    pharma_id TEXT NOT NULL,
    extracted_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    payload JSONB NOT NULL
);

CREATE TABLE IF NOT EXISTS staging.purchases_raw (
    id BIGSERIAL PRIMARY KEY,
    pharma_id TEXT NOT NULL,
    extracted_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    payload JSONB NOT NULL
);

CREATE TABLE IF NOT EXISTS mart.sales_daily (
    id BIGSERIAL PRIMARY KEY,
    pharma_id TEXT NOT NULL,
    sales_date DATE NOT NULL,
    gross_revenue NUMERIC,
    estimated_margin NUMERIC,
    ticket_count INTEGER,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS mart.top_products (
    id BIGSERIAL PRIMARY KEY,
    pharma_id TEXT NOT NULL,
    sales_date DATE NOT NULL,
    product_code TEXT,
    product_name TEXT,
    quantity NUMERIC,
    revenue NUMERIC,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS mart.stock_status (
    id BIGSERIAL PRIMARY KEY,
    pharma_id TEXT NOT NULL,
    snapshot_date DATE NOT NULL,
    product_code TEXT,
    product_name TEXT,
    stock_qty NUMERIC,
    coverage_days NUMERIC,
    status TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS mart.purchase_price_changes (
    id BIGSERIAL PRIMARY KEY,
    pharma_id TEXT NOT NULL,
    product_code TEXT,
    previous_price NUMERIC,
    latest_price NUMERIC,
    change_pct NUMERIC,
    detected_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS rag.documents (
    id BIGSERIAL PRIMARY KEY,
    pharma_id TEXT NOT NULL,
    source_path TEXT NOT NULL,
    content TEXT NOT NULL,
    embedding VECTOR(128),
    metadata JSONB,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_sales_raw_pharma ON staging.sales_raw (pharma_id);
CREATE INDEX IF NOT EXISTS idx_products_raw_pharma ON staging.products_raw (pharma_id);
CREATE INDEX IF NOT EXISTS idx_stock_raw_pharma ON staging.stock_raw (pharma_id);
CREATE INDEX IF NOT EXISTS idx_purchases_raw_pharma ON staging.purchases_raw (pharma_id);

CREATE INDEX IF NOT EXISTS idx_sales_daily_pharma_date ON mart.sales_daily (pharma_id, sales_date);
CREATE INDEX IF NOT EXISTS idx_top_products_pharma_date ON mart.top_products (pharma_id, sales_date);
CREATE INDEX IF NOT EXISTS idx_stock_status_pharma_date ON mart.stock_status (pharma_id, snapshot_date);
CREATE INDEX IF NOT EXISTS idx_purchase_price_pharma ON mart.purchase_price_changes (pharma_id);

CREATE INDEX IF NOT EXISTS idx_rag_documents_embedding ON rag.documents USING ivfflat (embedding vector_l2_ops) WITH (lists = 100);
