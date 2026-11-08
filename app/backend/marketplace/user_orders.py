"""Backend order authorization shared by the self-service MCP tools.

The caller supplies a verified subject, never a model-selected buyer or seller.
Each query resolves the current account and applies ownership before reading rows.
"""

import json
import logging
from pathlib import Path

from mcp.server.mcpserver.exceptions import ToolError
from sqlalchemy import select, text

from .db import Item, Listing, Order, Product, Session, Shipment, User

logger = logging.getLogger(__name__)


class OrderAccess:
    def __init__(self, issuer, identity_links_file, *, session_factory=Session):
        self.issuer = issuer
        self.identity_links_file = Path(identity_links_file)
        self.session_factory = session_factory

    def account(self, db, principal):
        # Read on each operation so removing a link takes effect for existing tokens.
        links = json.loads(self.identity_links_file.read_text())
        if principal.issuer != self.issuer or 'orders:read' not in principal.scopes:
            raise ToolError('Account access unavailable')
        if links.get('issuer') != self.issuer:
            raise ToolError('Account access unavailable')
        account_id = links.get('subjects', {}).get(principal.subject)
        account = db.get(User, account_id) if account_id else None
        if account is None or account.role not in ('buyer', 'seller'):
            raise ToolError('Account access unavailable')
        if account.role == 'seller' and not account.seller_id:
            raise ToolError('Account access unavailable')
        return account

    def profile(self, principal):
        with self.session_factory() as db:
            db.execute(text('SET TRANSACTION READ ONLY'))
            account = self.account(db, principal)
            return {'id': principal.subject, 'name': account.username, 'nickname': account.role}

    def orders(self, principal, *, order_id=None, limit=20, offset=0):
        if not 1 <= limit <= 50 or not 0 <= offset <= 10000:
            raise ToolError('Invalid pagination')
        with self.session_factory() as db:
            db.execute(text('SET TRANSACTION ISOLATION LEVEL REPEATABLE READ READ ONLY'))
            account = self.account(db, principal)
            statement = select(Order)
            if account.role == 'buyer':
                statement = statement.where(Order.customer_id == account.id)
            else:
                statement = statement.where(Order.id.in_(
                    select(Item.order_id).where(Item.seller_id == account.seller_id)
                ))
            if order_id is not None:
                statement = statement.where(Order.id == order_id)
            statement = statement.order_by(Order.created_at.desc(), Order.id).offset(offset).limit(limit + 1)
            records = db.scalars(statement).all()
            has_more = len(records) > limit
            records = records[:limit]
            orders = {
                order.id: {
                    'order_id': order.id,
                    'order_status': order.status,
                    'created_at': order.created_at.isoformat(),
                    'items': [],
                }
                for order in records
            }
            lines = (
                select(Item, Product.name, Shipment.status, Shipment.delivered_at)
                .join(Listing, Listing.id == Item.listing_id)
                .join(Product, Product.id == Listing.product_id)
                .outerjoin(Shipment, Shipment.item_id == Item.id)
                .where(Item.order_id.in_(list(orders)))
                .order_by(Item.order_id, Item.id)
            )
            if account.role == 'seller':
                lines = lines.where(Item.seller_id == account.seller_id)
            for item, product_name, shipment_status, delivered_at in db.execute(lines):
                orders[item.order_id]['items'].append({
                    'item_id': item.id,
                    'product': product_name,
                    'quantity': item.quantity,
                    'shipment_status': shipment_status,
                    'delivered_at': delivered_at.isoformat() if delivered_at else None,
                })
            logger.info('Scoped order read account=%s role=%s client=%s returned_orders=%d',
                        account.id, account.role, principal.client_id, len(orders))
            return {
                'orders': list(orders.values()),
                'next_offset': offset + limit if has_more else None,
            }
