from app import get_db
from app.models.authz import User, Role, Permission, RolePermission, Group, GroupRole, UserGroup
from app.models.order import Order
from app.models.print_job import PrintJob
from app.models.purchase_order import PurchaseOrder
from app.models.repair_ticket import RepairTicket
from app.models.accounting_transaction import AccountingTransaction
from app.models.catalog_item import CatalogItem
from sqlalchemy import select


def _login(client, email, password):
    r = client.post('/iam/auth/login', json={'email': email, 'password': password})
    assert r.status_code == 200
    return r.get_json()['access_token']


def _ensure_perm(session, code):
    p = session.execute(select(Permission).where(Permission.code==code)).scalar_one_or_none()
    if p:
        return p
    svc, action = code.split('.', 1)
    p = Permission(code=code, service=svc, action=action, description_i18n={'en': code})
    session.add(p); session.flush(); return p


def test_reports_metrics_aggregation_and_branch_scope(client):
    session = get_db()
    try:
        session.rollback()
    except Exception:
        pass
    # Clear existing rows to ensure deterministic counts
    session.query(Order).delete()
    session.query(PrintJob).delete()
    session.query(PurchaseOrder).delete()
    session.query(RepairTicket).delete()
    session.query(AccountingTransaction).delete()
    session.query(CatalogItem).delete()
    session.commit()
    # User with RPT.READ and necessary domain read perms (not strictly needed for metrics but future proof)
    u = User(name='RptUser', email='rpt@example.com', password_hash=''); u.set_password('pw'); session.add(u)
    r = Role(name='RptRole', is_system=False, description_i18n={'en': 'Reports'}); session.add(r); session.flush()
    for code in ['RPT.READ']:
        perm = _ensure_perm(session, code); session.add(RolePermission(role_id=r.id, permission_id=perm.id))
    g = Group(name='RptGroup', description_i18n={'en': 'B1'}, branch_scope={'allow': [1]}); session.add(g); session.flush()
    session.add(GroupRole(group_id=g.id, role_id=r.id)); session.add(UserGroup(user_id=u.id, group_id=g.id)); session.commit()
    token = _login(client, 'rpt@example.com', 'pw'); headers={'Authorization': f'Bearer {token}'}
    # Seed various domain records across branches (only branch 1 should count)
    o = Order(branch_id=1, customer_name='A', total_cents=100, status=Order.STATUS_NEW, created_by=u.id)
    pj = PrintJob(branch_id=1, product_id=None, status=PrintJob.STATUS_QUEUED, created_by=u.id)
    po = PurchaseOrder(branch_id=1, vendor_name='V', total_cents=50, status=PurchaseOrder.STATUS_DRAFT, created_by=u.id)
    rt = RepairTicket(branch_id=1, customer_name='Cust', device_type='Phone', issue_summary='Broken', status=RepairTicket.STATUS_NEW, created_by=u.id)
    at = AccountingTransaction(branch_id=1, description='Txn', amount_cents=30, status=AccountingTransaction.STATUS_NEW, created_by=u.id)
    ci = CatalogItem(branch_id=1, name='Item', category='Cat', sku='SKU1', price_cents=500, status=CatalogItem.STATUS_ACTIVE, created_by=u.id)
    # Out of scope branch 2 records
    o2 = Order(branch_id=2, customer_name='B', total_cents=200, status=Order.STATUS_NEW, created_by=u.id)
    session.add_all([o, pj, po, rt, at, ci, o2]); session.commit()
    resp = client.get('/reports/metrics?limit=100', headers=headers)
    assert resp.status_code == 200
    body = resp.get_json()
    domains = {m['domain'] for m in body['data']}
    # Out of scope order should not contribute a second Order row if only one status present
    assert 'Order' in domains and 'PrintJob' in domains and 'PurchaseOrder' in domains and 'RepairTicket' in domains and 'AccountingTransaction' in domains and 'CatalogItem' in domains
    # Ensure counts reflect only branch 1
    for row in body['data']:
        if row['domain'] == 'Order' and row['status'] == Order.STATUS_NEW:
            assert row['count'] == 1
    # HEAD conditional check
    head_resp = client.head('/reports/metrics?limit=100', headers=headers)
    assert head_resp.status_code == 200
    etag = head_resp.headers.get('ETag'); assert etag
    not_mod = client.get('/reports/metrics?limit=100', headers={**headers, 'If-None-Match': etag})
    assert not_mod.status_code == 304


def test_reports_metrics_pagination(client):
    session = get_db()
    try:
        session.rollback()
    except Exception:
        pass
    # Reuse existing user or create
    u = session.query(User).filter_by(email='rptpag@example.com').one_or_none()
    if not u:
        u = User(name='RptPag', email='rptpag@example.com', password_hash=''); u.set_password('pw'); session.add(u)
    r = session.query(Role).filter_by(name='RptPagRole').one_or_none()
    if not r:
        r = Role(name='RptPagRole', is_system=False, description_i18n={'en':'Reports'}); session.add(r); session.flush()
        perm = _ensure_perm(session, 'RPT.READ'); session.add(RolePermission(role_id=r.id, permission_id=perm.id))
    g = session.query(Group).filter_by(name='RptPagGroup').one_or_none()
    if not g:
        g = Group(name='RptPagGroup', description_i18n={'en': 'B1'}, branch_scope={'allow': [1]}); session.add(g); session.flush(); session.add(GroupRole(group_id=g.id, role_id=r.id)); session.add(UserGroup(user_id=u.id, group_id=g.id))
    session.commit()
    token = _login(client, 'rptpag@example.com', 'pw'); headers={'Authorization': f'Bearer {token}'}
    # Seed multiple statuses to enlarge metric rows
    session.add(Order(branch_id=1, customer_name='C1', total_cents=10, status=Order.STATUS_NEW, created_by=u.id))
    session.add(Order(branch_id=1, customer_name='C2', total_cents=20, status=Order.STATUS_APPROVED, created_by=u.id))
    session.add(PrintJob(branch_id=1, product_id=None, status=PrintJob.STATUS_QUEUED, created_by=u.id))
    session.add(PrintJob(branch_id=1, product_id=None, status=PrintJob.STATUS_STARTED, created_by=u.id))
    session.commit()
    first = client.get('/reports/metrics?limit=2&offset=0', headers=headers).get_json()
    second = client.get('/reports/metrics?limit=2&offset=2', headers=headers).get_json()
    assert first['pagination']['returned'] == 2
    assert second['pagination']['returned'] >= 1