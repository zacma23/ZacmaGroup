"""
Pytest integration tests for RAG schema existence.
These tests are safe to run in CI against a disposable/Postgres instance.
Requires DATABASE_URL env var, e.g. postgres://user:pass@localhost:5432/testdb

These are lightweight checks verifying the migration created expected schemas and tables.
"""
import os
import pytest
from sqlalchemy import create_engine, inspect, text

DATABASE_URL = os.environ.get('DATABASE_URL')

pytestmark = pytest.mark.skipif(DATABASE_URL is None, reason="DATABASE_URL not set")

EXPECTED_SCHEMAS = ['public', 'rag', 'audit', 'ai', 'admin']
EXPECTED_TABLES = {
    'public': ['tenants', 'users'],
    'rag': ['documents', 'document_chunks', 'embeddings', 'ingestion_jobs'],
    'audit': ['ingestion_audit'],
    'ai': ['retrieval_logs'],
    'admin': ['access_policies'],
}


@pytest.fixture(scope='module')
def engine():
    eng = create_engine(DATABASE_URL)
    yield eng
    eng.dispose()


def test_schemas_exist(engine):
    insp = inspect(engine)
    schemas = insp.get_schema_names()
    for s in EXPECTED_SCHEMAS:
        assert s in schemas, f"Schema {s} not found in database"


def test_tables_exist(engine):
    conn = engine.connect()
    insp = inspect(engine)
    for schema, tables in EXPECTED_TABLES.items():
        existing = insp.get_table_names(schema=schema)
        for t in tables:
            assert t in existing, f"Table {schema}.{t} missing"
    conn.close()


def test_pgvector_extension_present(engine):
    with engine.connect() as conn:
        res = conn.execute(text("SELECT extname FROM pg_extension WHERE extname IN ('vector','pgcrypto')"))
        names = {row[0] for row in res}
        assert 'vector' in names and 'pgcrypto' in names, "Required extensions (vector, pgcrypto) not installed"
