"""Read-only lookup regression tests; no fixtures or marketplace records change."""
import os
import psycopg
from psycopg.rows import dict_row
import pytest
from marketplace.tools import validate_sql

# The exact spelling/punctuation combinations that failed during the live demo.
NORMALIZED = "REPLACE(REPLACE(REPLACE(REPLACE(LOWER({value}), '&', 'and'), 'company', 'co'), '.', ''), ' ', '')"
CANDIDATES = """(VALUES
 ('seller','seller-1','Cedar & Co.'),
 ('seller','seller-2','Northstar Goods'),
 ('product','product-1','Cedar Planter')
) AS candidates(entity_type,entity_id,name)"""

@pytest.fixture
def reader():
    with psycopg.connect(os.environ['READ_DATABASE_URL'], row_factory=dict_row) as conn:
        conn.execute('BEGIN READ ONLY')
        yield conn

@pytest.mark.parametrize('name',['cedar&co','CEDAR & CO.','Cedar and Co','Cedar & Company','Cedar and Company'])
def test_normalized_name_variants_match_the_same_candidate(reader,name):
    sql = f"SELECT entity_type,entity_id,name FROM {CANDIDATES} WHERE {NORMALIZED.format(value='name')} = {NORMALIZED.format(value='%(name)s')}"
    rows = reader.execute(validate_sql(sql), {'name':name}).fetchall()
    assert rows == [{'entity_type':'seller','entity_id':'seller-1','name':'Cedar & Co.'}]


def test_partial_lookup_retains_seller_and_product_candidates(reader):
    sql = f'SELECT entity_type,entity_id,name FROM {CANDIDATES} WHERE name ILIKE %(name)s ORDER BY entity_type,entity_id'
    rows = reader.execute(validate_sql(sql), {'name':'%cedar%'}).fetchall()
    assert {(r['entity_type'],r['entity_id']) for r in rows} == {('seller','seller-1'),('product','product-1')}


def test_normalization_does_not_hide_ambiguous_names(reader):
    candidates="(VALUES ('seller','s1','Cedar & Co.'),('seller','s2','Cedar and Company')) AS candidates(entity_type,entity_id,name)"
    sql=f"SELECT entity_type,entity_id,name FROM {candidates} WHERE {NORMALIZED.format(value='name')} = {NORMALIZED.format(value='%(name)s')} ORDER BY entity_id"
    assert [r['entity_id'] for r in reader.execute(validate_sql(sql),{'name':'cedar&co'}).fetchall()] == ['s1','s2']


@pytest.mark.parametrize('sql',[
    "SELECT REPLACE(pg_read_file('/etc/passwd'),'a','b')",
    "SELECT REPLACE(CAST(pg_sleep(1) AS TEXT),'a','b')",
    "SELECT REPLACE(name,'a','b') FROM public.users",
    "WITH changed AS (DELETE FROM orders RETURNING name) SELECT REPLACE(name,'a','b') FROM changed",
])
def test_text_normalization_keeps_read_only_function_and_table_limits(sql):
    with pytest.raises(ValueError):validate_sql(sql)
