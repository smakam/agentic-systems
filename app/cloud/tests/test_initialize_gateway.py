"""Real PostgreSQL checks; INITIALIZER_TEST_ADMIN_URL must target a disposable DB.

The tests create fixed runtime roles and a database owned by a non-superuser,
so use a fresh PostgreSQL container rather than an application database.
"""
import importlib.util
import os
from pathlib import Path
import unittest

from sqlalchemy import create_engine, text
from sqlalchemy.engine import make_url
from sqlalchemy.exc import ProgrammingError

SCRIPT = Path(__file__).resolve().parents[1] / 'scripts' / 'initialize.py'
spec = importlib.util.spec_from_file_location('initialize', SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


@unittest.skipUnless(os.environ.get('INITIALIZER_TEST_ADMIN_URL'), 'requires disposable PostgreSQL')
class GatewayPermissions(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        admin_url = make_url(os.environ['INITIALIZER_TEST_ADMIN_URL'])
        cls.admin = create_engine(admin_url, isolation_level='AUTOCOMMIT')
        with cls.admin.connect() as conn:
            conn.execute(text("CREATE ROLE bootstrap LOGIN PASSWORD 'disposable-local-only' NOSUPERUSER"))
            for role in module.RUNTIME_ROLES:
                conn.execute(text(f'CREATE ROLE "{role}" NOSUPERUSER'))
            conn.execute(text('CREATE DATABASE initializer_gateway_test OWNER bootstrap'))
        cls.url = admin_url.set(username='bootstrap', password='disposable-local-only',
                                database='initializer_gateway_test')
        cls.bootstrap = create_engine(cls.url)
        cls.fixture = create_engine(admin_url.set(database='initializer_gateway_test'))

    @classmethod
    def tearDownClass(cls):
        cls.bootstrap.dispose()
        cls.fixture.dispose()
        with cls.admin.connect() as conn:
            conn.execute(text('DROP DATABASE initializer_gateway_test'))
            for role in (*module.RUNTIME_ROLES, 'bootstrap'):
                conn.execute(text(f'DROP ROLE "{role}"'))
        cls.admin.dispose()

    def setUp(self):
        with self.fixture.begin() as conn:
            conn.execute(text('DROP SCHEMA public CASCADE'))
            conn.execute(text('CREATE SCHEMA public AUTHORIZATION bootstrap'))
            conn.execute(text('GRANT USAGE, CREATE ON SCHEMA public TO litellm'))
            conn.execute(text('SET LOCAL ROLE litellm'))
            conn.execute(text('CREATE TABLE public._prisma_migrations (id integer PRIMARY KEY)'))
            conn.execute(text('INSERT INTO public._prisma_migrations VALUES (42)'))
            conn.execute(text('CREATE SEQUENCE public.gateway_sequence'))

    def grant_as_owner(self, sql):
        with self.fixture.begin() as conn:
            conn.execute(text('SET LOCAL ROLE litellm'))
            conn.execute(text(sql))

    def test_repeated_initialization_preserves_runtime_tables_and_permissions(self):
        # Reproduce the original Cloud SQL failure before exercising the fix.
        with self.assertRaisesRegex(ProgrammingError, 'permission denied.*_prisma_migrations'):
            with self.bootstrap.begin() as conn:
                conn.execute(text('REVOKE ALL ON ALL TABLES IN SCHEMA public FROM PUBLIC'))
        with self.bootstrap.begin() as conn:
            self.assertFalse(conn.execute(text(
                'SELECT rolsuper FROM pg_roles WHERE rolname = current_user')).scalar_one())
            conn.execute(text('CREATE TABLE public.bootstrap_table (id integer)'))
            conn.execute(text('CREATE SEQUENCE public.bootstrap_sequence'))
            conn.execute(text('GRANT SELECT ON public.bootstrap_table TO PUBLIC, market'))
            conn.execute(text('GRANT USAGE ON public.bootstrap_sequence TO agent_reader'))
        module.initialize_gateway(self.url)
        module.initialize_gateway(self.url)
        with self.fixture.begin() as conn:
            self.assertEqual(conn.execute(text('SELECT id FROM public._prisma_migrations')).scalar_one(), 42)
            for role in module.RUNTIME_ROLES[:-1]:
                for table in ('_prisma_migrations', 'bootstrap_table'):
                    self.assertFalse(conn.execute(text(
                        "SELECT has_table_privilege(:role, :table, 'SELECT')"),
                        {'role': role, 'table': f'public.{table}'}).scalar_one())
                self.assertFalse(conn.execute(text(
                    "SELECT has_sequence_privilege(:role, 'public.bootstrap_sequence', 'USAGE')"),
                    {'role': role}).scalar_one())
            conn.execute(text('SET LOCAL ROLE litellm'))
            conn.execute(text('CREATE TABLE public.new_runtime_table (id integer)'))
            conn.execute(text('INSERT INTO public._prisma_migrations VALUES (43)'))

    def test_unexpected_table_column_and_sequence_grants_fail_closed(self):
        for grant in (
            'GRANT SELECT ON public._prisma_migrations TO PUBLIC',
            'GRANT SELECT ON public._prisma_migrations TO agent_reader',
            'GRANT SELECT (id) ON public._prisma_migrations TO market',
            'GRANT USAGE ON public.gateway_sequence TO mcp_registry',
        ):
            with self.subTest(grant=grant):
                self.setUp()
                self.grant_as_owner(grant)
                with self.assertRaisesRegex(RuntimeError, 'unexpected grants'):
                    module.initialize_gateway(self.url)
                # Failure rolls back schema mutations; no permissions were widened.
                with self.fixture.connect() as conn:
                    self.assertFalse(conn.execute(text(
                        "SELECT has_schema_privilege('market', 'public', 'CREATE')")).scalar_one())

    def test_unexpected_object_owner_fails_closed(self):
        with self.fixture.begin() as conn:
            conn.execute(text('CREATE TABLE public.unknown_owner (id integer)'))
        with self.assertRaisesRegex(RuntimeError, 'must be owned'):
            module.initialize_gateway(self.url)


if __name__ == '__main__':
    unittest.main()
