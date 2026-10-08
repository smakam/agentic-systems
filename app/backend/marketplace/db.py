"""PostgreSQL business schema; explicit tables preserve domain grain."""
import os
from datetime import datetime, timezone
from sqlalchemy import create_engine, String, Integer, DateTime, JSON, ForeignKey, Text, UniqueConstraint, CheckConstraint, text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker
from pgvector.sqlalchemy import Vector

class Base(DeclarativeBase): pass
class User(Base):
    __tablename__ = 'users'
    id: Mapped[str] = mapped_column(String, primary_key=True)
    username: Mapped[str] = mapped_column(String, unique=True)
    password_hash: Mapped[str]
    role: Mapped[str]
    seller_id: Mapped[str | None]
class Login(Base):
    __tablename__ = 'logins'
    token_hash: Mapped[str] = mapped_column(String, primary_key=True)
    user_id: Mapped[str] = mapped_column(ForeignKey('users.id'))
    csrf: Mapped[str]
    expires: Mapped[datetime] = mapped_column(DateTime(timezone=True))
class State(Base):
    __tablename__ = 'state'
    id: Mapped[int] = mapped_column(primary_key=True)
    revision: Mapped[int] = mapped_column(default=1)
    clock: Mapped[datetime] = mapped_column(DateTime(timezone=True))
class Seller(Base):
    __tablename__ = 'sellers'
    id: Mapped[str] = mapped_column(primary_key=True)
    name: Mapped[str]
class Product(Base):
    __tablename__ = 'products'
    id: Mapped[str] = mapped_column(primary_key=True)
    name: Mapped[str]
    category: Mapped[str]
class Listing(Base):
    __tablename__ = 'listings'
    id: Mapped[str] = mapped_column(primary_key=True)
    seller_id: Mapped[str] = mapped_column(ForeignKey('sellers.id'))
    product_id: Mapped[str] = mapped_column(ForeignKey('products.id'))
    price: Mapped[int]
    stock: Mapped[int]
    __table_args__ = (CheckConstraint('price > 0 AND stock >= 0'),)
class Order(Base):
    __tablename__ = 'orders'
    id: Mapped[str] = mapped_column(primary_key=True)
    customer_id: Mapped[str] = mapped_column(ForeignKey('users.id'))
    status: Mapped[str]
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
class Item(Base):
    __tablename__ = 'order_items'
    id: Mapped[str] = mapped_column(primary_key=True)
    order_id: Mapped[str] = mapped_column(ForeignKey('orders.id'))
    listing_id: Mapped[str] = mapped_column(ForeignKey('listings.id'))
    seller_id: Mapped[str] = mapped_column(ForeignKey('sellers.id'))
    quantity: Mapped[int]
    unit_price: Mapped[int]
    __table_args__ = (CheckConstraint('quantity > 0 AND unit_price > 0'),)
class Payment(Base):
    __tablename__ = 'payments'
    id: Mapped[str] = mapped_column(primary_key=True)
    order_id: Mapped[str] = mapped_column(ForeignKey('orders.id'), unique=True)
    amount: Mapped[int]
    status: Mapped[str]
    currency: Mapped[str] = mapped_column(default='INR')
class Shipment(Base):
    __tablename__ = 'shipments'
    id: Mapped[str] = mapped_column(primary_key=True)
    item_id: Mapped[str] = mapped_column(ForeignKey('order_items.id'), unique=True)
    quantity: Mapped[int]
    status: Mapped[str]
    delivered_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
class Allocation(Base):
    __tablename__ = 'allocations'
    id: Mapped[str] = mapped_column(primary_key=True)
    item_id: Mapped[str] = mapped_column(ForeignKey('order_items.id'), unique=True)
    payment_id: Mapped[str] = mapped_column(ForeignKey('payments.id'))
    gross: Mapped[int]
    fee: Mapped[int]
    refunded: Mapped[int] = mapped_column(default=0)
    policy: Mapped[str] = mapped_column(default='settlement-v1')
class Payout(Base):
    __tablename__ = 'payouts'
    id: Mapped[str] = mapped_column(primary_key=True)
    allocation_id: Mapped[str] = mapped_column(ForeignKey('allocations.id'), unique=True)
    amount: Mapped[int] = mapped_column(default=0)
    status: Mapped[str] = mapped_column(default='held')
class Return(Base):
    __tablename__ = 'returns'
    id: Mapped[str] = mapped_column(primary_key=True)
    item_id: Mapped[str] = mapped_column(ForeignKey('order_items.id'))
    quantity: Mapped[int]
    status: Mapped[str]
class Refund(Base):
    __tablename__ = 'refunds'
    id: Mapped[str] = mapped_column(primary_key=True)
    return_id: Mapped[str] = mapped_column(ForeignKey('returns.id'), unique=True)
    payment_id: Mapped[str] = mapped_column(ForeignKey('payments.id'))
    amount: Mapped[int]
    status: Mapped[str]
class Event(Base):
    __tablename__ = 'events'
    id: Mapped[str] = mapped_column(primary_key=True)
    entity_id: Mapped[str]
    kind: Mapped[str]
    occurred_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    recorded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    revision: Mapped[int]
    details: Mapped[dict] = mapped_column(JSON)
class Command(Base):
    __tablename__ = 'commands'
    id: Mapped[str] = mapped_column(primary_key=True)
    actor_id: Mapped[str]
    fingerprint: Mapped[str]
    result: Mapped[dict] = mapped_column(JSON)
class Ticket(Base):
    __tablename__ = 'tickets'
    id: Mapped[str] = mapped_column(primary_key=True)
    order_id: Mapped[str] = mapped_column(ForeignKey('orders.id'))
    subject: Mapped[str]
    status: Mapped[str]
    message: Mapped[str] = mapped_column(Text)
class Incident(Base):
    __tablename__ = 'incidents'
    id: Mapped[str] = mapped_column(primary_key=True)
    title: Mapped[str]
    status: Mapped[str]
    affected_ids: Mapped[list] = mapped_column(JSON)
    evidence: Mapped[str]
class Document(Base):
    __tablename__ = 'document_chunks'
    id: Mapped[str] = mapped_column(primary_key=True)
    title: Mapped[str]
    version: Mapped[str]
    scope: Mapped[str]
    effective_from: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    effective_to: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    source: Mapped[str]
    line_start: Mapped[int]
    line_end: Mapped[int]
    body: Mapped[str] = mapped_column(Text)
    content_hash: Mapped[str]
    embedding_model: Mapped[str | None]
    embedding: Mapped[list | None] = mapped_column(Vector(1536))
class Conversation(Base):
    __tablename__ = 'conversations'
    id: Mapped[str] = mapped_column(primary_key=True)
    owner_id: Mapped[str] = mapped_column(ForeignKey('users.id'))
    title: Mapped[str]
    items: Mapped[list] = mapped_column(JSON, default=list)
class Run(Base):
    __tablename__ = 'runs'
    id: Mapped[str] = mapped_column(primary_key=True)
    conversation_id: Mapped[str] = mapped_column(ForeignKey('conversations.id'))
    revision: Mapped[int]
    question: Mapped[str] = mapped_column(Text)
    answer: Mapped[str] = mapped_column(Text, default='')
    status: Mapped[str]
    evidence: Mapped[dict] = mapped_column(JSON, default=dict)
    metrics: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))

class AnswerFeedback(Base):
    __tablename__ = 'answer_feedback'
    run_id: Mapped[str] = mapped_column(ForeignKey('runs.id'), primary_key=True)
    user_id: Mapped[str] = mapped_column(ForeignKey('users.id'))
    rating: Mapped[str]
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    __table_args__ = (CheckConstraint("rating IN ('up','down')"),)

class Memory(Base):
    __tablename__ = 'agent_memories'
    id: Mapped[str] = mapped_column(primary_key=True)
    owner_id: Mapped[str] = mapped_column(ForeignKey('users.id'), index=True)
    kind: Mapped[str]
    title: Mapped[str] = mapped_column(String(120))
    content: Mapped[str] = mapped_column(Text)
    version: Mapped[int] = mapped_column(default=1)
    source_conversation_id: Mapped[str] = mapped_column(ForeignKey('conversations.id'))
    source_run_id: Mapped[str | None] = mapped_column(ForeignKey('runs.id'))
    provenance: Mapped[dict] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    __table_args__ = (CheckConstraint("kind IN ('semantic','episodic','procedural') AND version > 0"),)

URL = os.getenv('DATABASE_URL', 'postgresql+psycopg://market:market-local@localhost:55432/market')
engine = create_engine(URL, pool_pre_ping=True,
                       pool_size=int(os.getenv('DB_POOL_SIZE','5')),
                       max_overflow=int(os.getenv('DB_MAX_OVERFLOW','10')))
Session = sessionmaker(engine, expire_on_commit=False)
BUSINESS_TABLES = [Seller, Product, Listing, Order, Item, Payment, Shipment, Allocation, Payout, Return, Refund, Event, Ticket, Incident]

def init_schema():
    with engine.begin() as conn:
        conn.execute(text('CREATE EXTENSION IF NOT EXISTS vector'))
        conn.execute(text('CREATE TABLE IF NOT EXISTS schema_migrations (version INTEGER PRIMARY KEY, installed_at TIMESTAMPTZ DEFAULT now())'))
        version=conn.execute(text('SELECT max(version) FROM schema_migrations')).scalar()
        if version not in (None,1): raise RuntimeError('Unsupported database schema version; apply an explicit migration')
        conn.execute(text('INSERT INTO schema_migrations(version) VALUES (1) ON CONFLICT DO NOTHING'))
    Base.metadata.create_all(engine)
    with engine.begin() as conn:
        conn.execute(text('CREATE SCHEMA IF NOT EXISTS analytics'))
        for model in BUSINESS_TABLES:
            name = model.__tablename__
            conn.execute(text(f'CREATE OR REPLACE VIEW analytics.{name} AS SELECT * FROM public.{name}'))
        conn.execute(text('CREATE OR REPLACE VIEW analytics.customers AS SELECT id, username FROM public.users WHERE role = \'buyer\''))
        conn.execute(text('CREATE OR REPLACE VIEW analytics.freshness AS SELECT revision, clock FROM public.state'))
        conn.execute(text("CREATE OR REPLACE VIEW analytics.seller_balances AS SELECT s.id AS seller_id, s.name, COALESCE(SUM(a.gross),0) AS captured, COALESCE(SUM(a.refunded),0) AS refunded, COALESCE(SUM(a.fee),0) AS fees, COALESCE(SUM(CASE WHEN p.status='completed' THEN p.amount ELSE 0 END),0) AS paid_out, COALESCE(SUM(CASE WHEN p.status<>'completed' THEN a.gross-a.fee-a.refunded ELSE 0 END),0) AS unpaid FROM public.sellers s LEFT JOIN public.order_items i ON i.seller_id=s.id LEFT JOIN public.allocations a ON a.item_id=i.id LEFT JOIN public.payouts p ON p.allocation_id=a.id GROUP BY s.id,s.name"))
        conn.execute(text('GRANT USAGE ON SCHEMA analytics TO agent_reader'))
        conn.execute(text('GRANT SELECT ON ALL TABLES IN SCHEMA analytics TO agent_reader'))
        conn.execute(text('GRANT SELECT ON document_chunks TO agent_reader'))
