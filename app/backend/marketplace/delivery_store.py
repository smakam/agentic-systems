"""Durable records owned by the simulated delivery service, not marketplace.

The simulator uses its own SQLite file/volume. No real carrier is contacted.
Booking is unique by marketplace shipment, and delivery updates are repeat-safe.
"""
import hashlib
import json
import os
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timedelta, timezone
from pathlib import Path


class DeliveryRecordError(ValueError):
    pass


def aware_time(value):
    try:
        when = datetime.fromisoformat(str(value).replace('Z', '+00:00'))
    except (ValueError, TypeError):
        raise DeliveryRecordError('Use an ISO simulation time with timezone') from None
    if when.tzinfo is None:
        raise DeliveryRecordError('Simulation time must include timezone')
    return when


class DeliveryStore:
    def __init__(self, path=None):
        self.path = str(path or os.getenv('DELIVERY_DATABASE_PATH', '/tmp/marketplace-delivery.sqlite3'))
        Path(self.path).parent.mkdir(parents=True, exist_ok=True)
        with self.connection() as db:
            db.execute('''CREATE TABLE IF NOT EXISTS delivery_shipments (
                reference TEXT PRIMARY KEY, marketplace_shipment_id TEXT UNIQUE NOT NULL,
                fixture TEXT NOT NULL, status TEXT NOT NULL, expected_delivery_at TEXT NOT NULL,
                reason TEXT, events TEXT NOT NULL, created_at TEXT NOT NULL, updated_at TEXT NOT NULL
            )''')
            db.execute('''CREATE TABLE IF NOT EXISTS delivery_fixture_operations (
                operation_key TEXT PRIMARY KEY, reference TEXT NOT NULL, fixture TEXT NOT NULL
            )''')

    @contextmanager
    def connection(self):
        conn = sqlite3.connect(self.path, timeout=10)
        conn.row_factory = sqlite3.Row
        try:
            with conn:
                yield conn
        finally:
            conn.close()

    @staticmethod
    def _json(row):
        if row is None:
            raise DeliveryRecordError('Delivery reference not found')
        data = dict(row)
        data['events'] = json.loads(data['events'])
        return data

    def book(self, shipment_id, fixture, clock):
        if not isinstance(shipment_id, str) or not 1 <= len(shipment_id) <= 120:
            raise DeliveryRecordError('A marketplace shipment identifier is required')
        if fixture not in ('normal', 'exception'):
            raise DeliveryRecordError('Choose normal or exception delivery fixture')
        now = aware_time(clock)
        reference = 'delivery-' + hashlib.sha256(shipment_id.encode()).hexdigest()[:24]
        status = 'in_transit' if fixture == 'normal' else 'exception'
        reason = None if fixture == 'normal' else 'The depot sorting scanner failed. The parcel is held at depot DEMO-17 for manual rerouting; no departure scan is recorded.'
        events = [dict(event='booked', at=now.isoformat(), detail='Simulated shipment accepted'),
                  dict(event=status, at=now.isoformat(), detail='Departed origin; next milestone is on schedule' if fixture == 'normal' else reason)]
        with self.connection() as db:
            # INSERT OR IGNORE plus unique shipment ID also handles concurrent
            # bookings and retries after a remote-success/local-rollback window.
            db.execute('INSERT OR IGNORE INTO delivery_shipments VALUES (?,?,?,?,?,?,?,?,?)',
                       (reference, shipment_id, fixture, status, (now + timedelta(hours=48)).isoformat(),
                        reason, json.dumps(events), now.isoformat(), now.isoformat()))
            row = self._json(db.execute('SELECT * FROM delivery_shipments WHERE marketplace_shipment_id=?', (shipment_id,)).fetchone())
            if row['fixture'] != fixture:
                raise DeliveryRecordError('This shipment already has a different delivery fixture')
        return self.status(reference, now.isoformat())

    def deliver(self, reference, clock):
        now = aware_time(clock)
        with self.connection() as db:
            db.execute('BEGIN IMMEDIATE')
            row = self._json(db.execute('SELECT * FROM delivery_shipments WHERE reference=?', (reference,)).fetchone())
            if row['status'] != 'delivered':
                if now < aware_time(row['created_at']):
                    raise DeliveryRecordError('Delivery time precedes booking time')
                events = [*row['events'], dict(event='delivered', at=now.isoformat(), detail='Seller manually simulated successful delivery')]
                db.execute('UPDATE delivery_shipments SET status=?, reason=NULL, events=?, updated_at=? WHERE reference=?',
                           ('delivered', json.dumps(events), now.isoformat(), reference))
        return self.status(reference, now.isoformat())

    def set_fixture(self, reference, fixture, clock, operation_key):
        """Manual scenario control; it never delivers a shipment or polls a carrier."""
        if fixture not in ('normal','exception'):
            raise DeliveryRecordError('Choose normal or exception delivery fixture')
        if not isinstance(operation_key,str) or not 8 <= len(operation_key) <= 160:
            raise DeliveryRecordError('A repeat-safe fixture operation key is required')
        now = aware_time(clock)
        with self.connection() as db:
            db.execute('BEGIN IMMEDIATE')
            row = self._json(db.execute('SELECT * FROM delivery_shipments WHERE reference=?',(reference,)).fetchone())
            if row['status'] == 'delivered':
                raise DeliveryRecordError('Delivered shipment fixture cannot change')
            if now < aware_time(row['created_at']):
                raise DeliveryRecordError('Scenario time precedes booking time')
            previous = db.execute('SELECT reference,fixture FROM delivery_fixture_operations WHERE operation_key=?',(operation_key,)).fetchone()
            if previous is not None:
                if previous['reference'] != reference or previous['fixture'] != fixture:
                    raise DeliveryRecordError('Fixture operation key already used for a different request')
                if row['fixture'] != fixture:
                    raise DeliveryRecordError('This fixture request was applied earlier but the shipment has since changed; refresh and use a new command')
            if row['fixture'] != fixture:
                status = 'in_transit' if fixture == 'normal' else 'exception'
                reason = None if fixture == 'normal' else 'The depot sorting scanner failed. The parcel is held at depot DEMO-17 for manual rerouting; no departure scan is recorded.'
                events = [*row['events'],dict(event=status,at=now.isoformat(),detail='Manual simulator control: resumed transit' if fixture == 'normal' else reason)]
                db.execute('UPDATE delivery_shipments SET fixture=?,status=?,reason=?,events=?,updated_at=? WHERE reference=?',
                    (fixture,status,reason,json.dumps(events),now.isoformat(),reference))
            db.execute('INSERT OR IGNORE INTO delivery_fixture_operations VALUES (?,?,?)',(operation_key,reference,fixture))
        return self.status(reference,now.isoformat())

    def status(self, reference, as_of):
        now = aware_time(as_of)
        with self.connection() as db:
            row = self._json(db.execute('SELECT * FROM delivery_shipments WHERE reference=?', (reference,)).fetchone())
        overdue = row['status'] != 'delivered' and now > aware_time(row['expected_delivery_at'])
        return dict(reference=row['reference'], marketplace_shipment_id=row['marketplace_shipment_id'],
                    status=row['status'], fixture=row['fixture'], expected_delivery_at=row['expected_delivery_at'],
                    delivered_at=row['updated_at'] if row['status'] == 'delivered' else None,
                    overdue=overdue, on_schedule=row['status'] == 'in_transit' and not overdue,
                    observed_at=datetime.now(timezone.utc).isoformat(), simulation_as_of=now.isoformat(),
                    source='simulated-delivery-service', simulated=True)

    def issue(self, reference, as_of):
        status = self.status(reference, as_of)
        with self.connection() as db:
            row = self._json(db.execute('SELECT * FROM delivery_shipments WHERE reference=?', (reference,)).fetchone())
        return dict(reference=reference, reason=row['reason'], tracking_events=row['events'],
                    overdue=status['overdue'], observed_at=status['observed_at'],
                    source='simulated-delivery-service', simulated=True,
                    note='No specific delay reason is recorded' if status['overdue'] and not row['reason'] else None)
