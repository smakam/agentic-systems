"""Versioned semantic catalog: database metadata, never business-record samples."""
import copy
import hashlib
import json
import sqlglot
from sqlglot import exp

CATALOG_VERSION = '2.0'
# Explicit lineage for views defined in db.init_schema. Aggregate views have no
# direct column lineage: do not infer their constraints from base tables.
DIRECT_VIEWS = {'sellers','products','listings','orders','order_items','payments',
                'shipments','allocations','payouts','returns','refunds','events','tickets','incidents'}
LINEAGE = {name: name for name in DIRECT_VIEWS} | {'customers': 'users', 'freshness': 'state'}


def build_catalog(conn, ontology):
    columns = conn.execute("""SELECT table_name,column_name,data_type
        FROM information_schema.columns WHERE table_schema='analytics'
        ORDER BY table_name,ordinal_position""").fetchall()
    # pg_catalog exposes constraints even when the reader has no SELECT on the
    # backing public tables. Filter these to explicitly mapped, exposed columns.
    attributes = conn.execute("""SELECT c.relname AS table_name,a.attname AS column_name,
        format_type(a.atttypid,a.atttypmod) AS sql_type,a.attnotnull AS not_null
        FROM pg_attribute a JOIN pg_class c ON c.oid=a.attrelid
        JOIN pg_namespace n ON n.oid=c.relnamespace
        WHERE n.nspname='public' AND a.attnum>0 AND NOT a.attisdropped
        ORDER BY c.relname,a.attnum""").fetchall()
    constraints = conn.execute("""SELECT c.relname AS table_name,k.contype AS kind,
        ARRAY(SELECT a.attname FROM unnest(k.conkey) WITH ORDINALITY AS u(num,ord)
          JOIN pg_attribute a ON a.attrelid=k.conrelid AND a.attnum=u.num ORDER BY u.ord) AS columns,
        pg_get_constraintdef(k.oid) AS definition
        FROM pg_constraint k JOIN pg_class c ON c.oid=k.conrelid
        JOIN pg_namespace n ON n.oid=c.relnamespace
        WHERE n.nspname='public' AND k.contype IN ('p','u','c')
        ORDER BY c.relname,k.conname""").fetchall()
    available = {}
    for column in columns:
        available.setdefault(column['table_name'], {})[column['column_name']] = column
    attrs = {(a['table_name'], a['column_name']): a for a in attributes}
    result = {k: copy.deepcopy(v) for k,v in ontology.items() if k not in ('version','entities')}
    result.update(catalog_version=CATALOG_VERSION, ontology_version=ontology['version'], entities={})
    issues = []
    views = {r['viewname']: r['definition'] for r in conn.execute(
        "SELECT viewname,definition FROM pg_views WHERE schemaname='analytics'").fetchall()}
    valid_lineage = set()
    for name, base in LINEAGE.items():
        tree = sqlglot.parse_one(views.get(name, 'SELECT 1'), read='postgres')
        tables = list(tree.find_all(exp.Table))
        direct_columns = all(isinstance(x, exp.Column) for x in tree.expressions)
        if (len(tables) == 1 and tables[0].name == base
                and tables[0].db == 'public' and direct_columns
                and not tree.args.get('joins') and not tree.args.get('group')
                and isinstance(tree, exp.Select)):
            valid_lineage.add(name)
        else:
            issues.append(f'View lineage differs from reviewed direct mapping: {name}')
    for name, entity in ontology['entities'].items():
        actual = available.get(name, {})
        if entity['table'] != f'analytics.{name}' or not actual:
            issues.append(f'Missing or mismatched table: {entity["table"]}')
        missing = set(entity['fields']) - set(actual)
        extra = set(actual) - set(entity['fields'])
        issues.extend(f'Missing database column: {name}.{field}' for field in sorted(missing))
        issues.extend(f'Column lacks semantic definition: {name}.{field}' for field in sorted(extra))
        merged = copy.deepcopy(entity)
        merged['fields'] = {}
        for field, meta in actual.items():
            base = LINEAGE.get(name) if name in valid_lineage else None
            attr = attrs.get((base, field))
            merged['fields'][field] = {
                'description': entity['fields'].get(field), 'data_type': meta['data_type'],
                'sql_type': attr['sql_type'] if attr else meta['data_type'],
                'nullable': not attr['not_null'] if attr else None,
                'type_source': 'database metadata',
                'nullability_source': f'public.{base}.{field} via explicit view lineage' if attr else 'unknown for derived view',
            }
        merged['constraints'] = [
            {'kind': {'p':'primary_key','u':'unique','c':'check'}[c['kind']],
             'columns': c['columns'], 'definition': c['definition'],
             'source': f'public.{LINEAGE[name]} via explicit view lineage'}
            for c in constraints if name in valid_lineage and c['table_name'] == LINEAGE[name]
            and c['columns'] and set(c['columns']) <= set(actual)
        ]
        if set(entity.get('key', [])) - set(actual):
            issues.append(f'Semantic key references missing columns: {name}')
        result['entities'][name] = merged
    for rel in ontology['relationships']:
        for end in ('from','to'):
            table, field = rel[end].split('.')
            if field not in available.get(table, {}):
                issues.append(f'Relationship references missing column: {rel[end]}')
    # Relationship meanings/cardinalities remain authored semantics, not inferred
    # view constraints. No unsupported claim of semantic or type-drift detection.
    result['validation'] = {'status': 'error' if issues else 'ok', 'issues': issues,
        'scope': 'table/field coverage and relationship/key endpoints; business meanings and cardinalities require review'}
    result['catalog_hash'] = hashlib.sha256(json.dumps(result, sort_keys=True).encode()).hexdigest()[:16]
    return result
