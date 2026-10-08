"""Explicit schema/seed job; bootstrap credentials are never runtime credentials."""
import argparse
import os
import subprocess
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.engine import make_url

APP_DATABASES = ('market', 'market_test', 'market_eval')
RUNTIME_ROLES = ('market', 'agent_reader', 'mcp_registry', 'litellm')


def harden_roles(engine):
    with engine.begin() as conn:
        existing = set(conn.execute(text('SELECT rolname FROM pg_roles')).scalars())
        if set(RUNTIME_ROLES) - existing:
            raise RuntimeError('Create the required runtime SQL users before initialization')
        # Cloud SQL postgres is not a PostgreSQL superuser. It cannot even set
        # NOSUPERUSER/NOREPLICATION/NOBYPASSRLS on already-safe roles. Refuse any
        # unexpectedly privileged role rather than accepting an unsafe setup.
        unsafe = conn.execute(text(
            'SELECT rolname FROM pg_roles WHERE rolname IN '
            "('market','agent_reader','mcp_registry','litellm') "
            'AND (rolsuper OR rolreplication OR rolbypassrls)'
        )).scalars().all()
        if unsafe:
            raise RuntimeError('Runtime SQL users have unsupported administrative privileges')
        for role in RUNTIME_ROLES:
            if 'cloudsqlsuperuser' in existing:
                conn.execute(text(f'REVOKE cloudsqlsuperuser FROM "{role}"'))
            conn.execute(text(f'ALTER ROLE "{role}" NOCREATEDB NOCREATEROLE NOINHERIT'))
        # Match the local reader contract. pg_views qualifies backing public
        # tables only when public is outside the reader's search path.
        conn.execute(text('ALTER ROLE agent_reader SET search_path = analytics'))
        conn.execute(text('ALTER ROLE agent_reader SET default_transaction_read_only = on'))
        conn.execute(text("ALTER ROLE agent_reader SET statement_timeout = '3000ms'"))
        memberships = conn.execute(text(
            'SELECT member FROM pg_auth_members WHERE member IN '
            "(SELECT oid FROM pg_roles WHERE rolname IN ('market','agent_reader','mcp_registry','litellm'))"
        )).all()
        if memberships:
            raise RuntimeError('Runtime SQL users must not retain other role memberships')
        for database in (*APP_DATABASES, 'litellm'):
            conn.execute(text(f'REVOKE ALL ON DATABASE "{database}" FROM PUBLIC'))
            for role in RUNTIME_ROLES:
                conn.execute(text(f'REVOKE ALL ON DATABASE "{database}" FROM "{role}"'))
            allowed = ('litellm',) if database == 'litellm' else RUNTIME_ROLES[:3]
            for role in allowed:
                conn.execute(text(f'GRANT CONNECT ON DATABASE "{database}" TO "{role}"'))


def initialize_database(url):
    # A fresh child process per DB ensures module-level engines target that DB.
    os.environ['DATABASE_URL'] = url.render_as_string(hide_password=False)
    from marketplace import db as schema
    from marketplace.seed import seed
    from marketplace.cloud_registry import DDL
    schema.init_schema()
    with schema.engine.begin() as conn:
        conn.execute(text(DDL))
        conn.execute(text('REVOKE ALL ON SCHEMA public, analytics FROM PUBLIC'))
        for role in RUNTIME_ROLES:
            conn.execute(text(f'REVOKE ALL ON SCHEMA public, analytics FROM "{role}"'))
            conn.execute(text(f'REVOKE ALL ON ALL TABLES IN SCHEMA public, analytics FROM "{role}"'))
            conn.execute(text(f'REVOKE ALL ON ALL SEQUENCES IN SCHEMA public, analytics FROM "{role}"'))
        conn.execute(text('REVOKE ALL ON ALL TABLES IN SCHEMA public, analytics FROM PUBLIC'))
        conn.execute(text('REVOKE ALL ON ALL SEQUENCES IN SCHEMA public, analytics FROM PUBLIC'))
        conn.execute(text('GRANT USAGE ON SCHEMA public TO market, agent_reader, mcp_registry'))
        conn.execute(text('GRANT USAGE ON SCHEMA analytics TO market, agent_reader'))
        conn.execute(text('GRANT SELECT ON ALL TABLES IN SCHEMA analytics TO market, agent_reader'))
        # Metadata allowlist excludes the migration and MCP registry tables.
        for table in schema.Base.metadata.sorted_tables:
            conn.execute(text(f'GRANT SELECT, INSERT, UPDATE, DELETE ON public."{table.name}" TO market'))
        conn.execute(text('GRANT SELECT ON public.document_chunks TO agent_reader'))
        conn.execute(text('GRANT SELECT, INSERT, UPDATE, DELETE ON public.mcp_investigations TO mcp_registry'))
    with schema.Session.begin() as session:
        seed(session)
    schema.engine.dispose()
    print(f'{url.database}: schema, synthetic seed and grants ready; existing data preserved.')


def initialize_gateway(url):
    engine = create_engine(url, pool_pre_ping=True)
    try:
        with engine.begin() as conn:
            conn.execute(text('REVOKE ALL ON SCHEMA public FROM PUBLIC'))
            for role in RUNTIME_ROLES:
                conn.execute(text(f'REVOKE ALL ON SCHEMA public FROM "{role}"'))
            objects = conn.execute(text("""
                SELECT c.oid, c.relname, c.relkind, owner.rolname AS owner,
                       owner.rolname = current_user AS bootstrap_owned
                FROM pg_class c
                JOIN pg_namespace n ON n.oid = c.relnamespace
                JOIN pg_roles owner ON owner.oid = c.relowner
                WHERE n.nspname = 'public' AND c.relkind IN ('r','p','v','m','f','S')
            """)).mappings().all()
            for obj in objects:
                if obj['bootstrap_owned']:
                    kind = 'SEQUENCE' if obj['relkind'] == 'S' else 'TABLE'
                    name = conn.dialect.identifier_preparer.quote_identifier(obj['relname'])
                    for role in ('PUBLIC', *RUNTIME_ROLES[:-1]):
                        conn.execute(text(f'REVOKE ALL ON {kind} public.{name} FROM {role}'))
                elif obj['owner'] != 'litellm':
                    raise RuntimeError('Gateway objects must be owned by bootstrap or litellm')
            # Cloud SQL's bootstrap user cannot revoke privileges on Prisma
            # objects owned by litellm. Inspect their ACLs instead, including
            # column grants, and refuse unexpected access without owner secrets.
            unexpected = conn.execute(text("""
                SELECT c.relname
                FROM pg_class c JOIN pg_namespace n ON n.oid = c.relnamespace
                CROSS JOIN LATERAL aclexplode(c.relacl) acl
                WHERE n.nspname = 'public' AND c.relkind IN ('r','p','v','m','f','S')
                  AND acl.grantee <> c.relowner
                  AND acl.grantee <> (SELECT oid FROM pg_roles WHERE rolname = 'litellm')
                UNION ALL
                SELECT c.relname
                FROM pg_class c JOIN pg_namespace n ON n.oid = c.relnamespace
                JOIN pg_attribute a ON a.attrelid = c.oid
                CROSS JOIN LATERAL aclexplode(a.attacl) acl
                WHERE n.nspname = 'public' AND c.relkind IN ('r','p','v','m','f','S')
                  AND acl.grantee <> c.relowner
                  AND acl.grantee <> (SELECT oid FROM pg_roles WHERE rolname = 'litellm')
                LIMIT 1
            """)).first()
            if unexpected:
                raise RuntimeError('Gateway objects have unexpected grants; the object owner must revoke them')
            # Prisma-created tables are owned by litellm. No other DB access.
            conn.execute(text('GRANT USAGE, CREATE ON SCHEMA public TO litellm'))
    finally:
        engine.dispose()
    print('litellm: dedicated database schema permissions ready.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--database', choices=APP_DATABASES)
    args = parser.parse_args()
    if not os.environ.get('DEMO_PASSWORD'):
        raise RuntimeError('DEMO_PASSWORD must come from the initialization secret')
    raw_url = os.environ.get('BOOTSTRAP_DATABASE_URL') or os.environ.get('DATABASE_URL')
    if not raw_url:
        raise RuntimeError('A bootstrap database URL is required')
    url = make_url(raw_url)
    if args.database:
        initialize_database(url.set(database=args.database))
        return
    engine = create_engine(url, pool_pre_ping=True)
    try:
        harden_roles(engine)
    finally:
        engine.dispose()
    for database in APP_DATABASES:
        subprocess.run([sys.executable, __file__, '--database', database], check=True)
    initialize_gateway(url.set(database='litellm'))
    print('Initialization complete. Runtime roles have no administrative SQL privileges.')


if __name__ == '__main__':
    main()
