from flask import Blueprint, request, abort
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from app.models.authz import User, Role, Permission, RolePermission, UserRole, Group, GroupRole, UserGroup
from app.models.audit import AuditLog
from sqlalchemy import select, delete
from app import get_db
from app.services.policy import compute_effective_permissions, assert_not_removing_last_owner, compute_branch_ids
from app.config.pagination import normalize_pagination
from app.utils.listing import handle_conditional, make_cached_list_response, compute_etag
from app.services.audit import add_audit  # legacy direct calls (will be phased out as decorator adopted)
from app.decorators.audit import audit_log
from app.decorators.auth import require_permissions

iam_bp = Blueprint('iam', __name__)

@iam_bp.get('/permissions')
@require_permissions('ADMIN.ROLE.MANAGE')
def list_permissions():
    session = get_db()
    q = session.query(Permission)
    try:
        limit, offset = normalize_pagination(request.args.get('limit'), request.args.get('offset'))
    except ValueError as e:
        abort(400, description=str(e))
    total = q.count()
    rows = q.order_by(Permission.id.asc()).offset(offset).limit(limit).all()
    payload = {
        'data': [
            {'id': p.id, 'code': p.code, 'service': p.service, 'action': p.action, 'description_i18n': p.description_i18n}
            for p in rows
        ],
        'pagination': {
            'total': total,
            'limit': limit,
            'offset': offset,
            'returned': len(rows)
        }
    }
    latest_ts = rows[0].updated_at if rows else None
    resp, etag = make_cached_list_response(payload['data'], total, limit, offset, latest_ts)
    cond = handle_conditional(etag, latest_ts)
    if cond:
        return cond
    return resp

@iam_bp.route('/permissions', methods=['HEAD'])
@require_permissions('ADMIN.ROLE.MANAGE')
def head_permissions():
    session = get_db()
    q = session.query(Permission)
    try:
        limit, offset = normalize_pagination(request.args.get('limit'), request.args.get('offset'))
    except ValueError as e:
        abort(400, description=str(e))
    total = q.count()
    rows = q.order_by(Permission.id.asc()).offset(offset).limit(limit).all()
    latest_ts = rows[0].updated_at if rows else None
    data = [
        {'id': p.id, 'code': p.code, 'service': p.service, 'action': p.action, 'description_i18n': p.description_i18n}
        for p in rows
    ]
    resp, etag = make_cached_list_response(data, total, limit, offset, latest_ts)
    cond = handle_conditional(etag, latest_ts)
    if cond:
        cond.set_data(b'')
        return cond
    resp.set_data(b'')
    return resp


@iam_bp.get('/roles')
@require_permissions('ADMIN.ROLE.MANAGE')
def list_roles():
    session = get_db()
    q = session.query(Role)
    # Basic pagination
    try:
        limit, offset = normalize_pagination(request.args.get('limit'), request.args.get('offset'))
    except ValueError as e:
        abort(400, description=str(e))
    total = q.count()
    rows = q.order_by(Role.id.asc()).offset(offset).limit(limit).all()
    payload = {
        'data': [
            {'id': r.id, 'name': r.name, 'is_system': r.is_system, 'permissions': [rp.permission.code for rp in r.permissions]}
            for r in rows
        ],
        'pagination': {
            'total': total,
            'limit': limit,
            'offset': offset,
            'returned': len(rows)
        }
    }
    latest_ts = rows[0].updated_at if rows else None
    resp, etag = make_cached_list_response(payload['data'], total, limit, offset, latest_ts)
    cond = handle_conditional(etag, latest_ts)
    if cond:
        return cond
    return resp

@iam_bp.route('/roles', methods=['HEAD'])
@require_permissions('ADMIN.ROLE.MANAGE')
def head_roles():
    session = get_db()
    q = session.query(Role)
    try:
        limit, offset = normalize_pagination(request.args.get('limit'), request.args.get('offset'))
    except ValueError as e:
        abort(400, description=str(e))
    total = q.count()
    rows = q.order_by(Role.id.asc()).offset(offset).limit(limit).all()
    latest_ts = rows[0].updated_at if rows else None
    data = [
        {'id': r.id, 'name': r.name, 'is_system': r.is_system, 'permissions': [rp.permission.code for rp in r.permissions]}
        for r in rows
    ]
    resp, etag = make_cached_list_response(data, total, limit, offset, latest_ts)
    cond = handle_conditional(etag, latest_ts)
    if cond:
        cond.set_data(b'')
        return cond
    resp.set_data(b'')
    return resp


@iam_bp.post('/roles')
@require_permissions('ADMIN.ROLE.MANAGE')
@audit_log('ROLE.CREATE', entity='Role', entity_id_key='id', meta_keys=['name'])
def create_role():
    data = request.json or {}
    name = data.get('name')
    if not name:
        abort(400, description='name required')
    session = get_db()
    if session.execute(select(Role).where(Role.name==name)).scalar_one_or_none():
        abort(400, description='role exists')
    role = Role(name=name, is_system=False, description_i18n=data.get('description_i18n') or {})
    session.add(role)
    session.commit()
    return {'id': role.id, 'name': role.name}, 201


@iam_bp.put('/roles/<int:role_id>/permissions')
@require_permissions('ADMIN.ROLE.MANAGE')
@audit_log(
    'ROLE.PERM.REPLACE',
    entity='Role',
    entity_id_key='id',
    meta_builder=lambda data, rv, a, kw: {'count': len(data.get('permissions', []))},
)
def replace_role_permissions(role_id: int):
    session = get_db()
    role = session.execute(select(Role).where(Role.id==role_id)).scalar_one_or_none()
    if not role:
        abort(404)
    data = request.json or {}
    codes = data.get('permissions') or []
    # Map codes → Permission objects
    perms = session.execute(select(Permission).where(Permission.code.in_(codes))).scalars().all()
    found_codes = {p.code for p in perms}
    missing = set(codes) - found_codes
    if missing:
        abort(400, description=f'Unknown permission codes: {sorted(missing)}')
    # Clear existing
    session.execute(delete(RolePermission).where(RolePermission.role_id==role.id))
    for p in perms:
        session.add(RolePermission(role_id=role.id, permission_id=p.id))
    session.commit()
    return {'id': role.id, 'permissions': codes}


@iam_bp.put('/users/<int:user_id>/roles')
@require_permissions('ADMIN.USER.MANAGE')
@audit_log('USER.ROLES.SET', entity='User', entity_id_key='user_id', meta_keys=['role_ids'])
def set_user_roles(user_id: int):
    session = get_db()
    user = session.execute(select(User).where(User.id==user_id)).scalar_one_or_none()
    if not user:
        abort(404)
    data = request.json or {}
    role_ids = set(data.get('role_ids') or [])
    # Validate roles exist
    roles = session.execute(select(Role).where(Role.id.in_(list(role_ids)))).scalars().all() if role_ids else []
    existing_ids = {r.id for r in roles}
    missing = role_ids - existing_ids
    if missing:
        abort(400, description=f'Unknown role ids: {sorted(missing)}')
    assert_not_removing_last_owner(user.id, role_ids)
    # Replace direct assignments
    session.execute(delete(UserRole).where(UserRole.user_id==user.id))
    for rid in role_ids:
        session.add(UserRole(user_id=user.id, role_id=rid))
    session.commit()
    return {'user_id': user.id, 'role_ids': sorted(role_ids)}


@iam_bp.post('/auth/login')
def login():
    data = request.json or {}
    email = data.get('email'); password = data.get('password')
    if not email or not password:
        abort(400, description='email & password required')
    session = get_db()
    user = session.execute(select(User).where(User.email==email)).scalar_one_or_none()
    if not user or not user.verify_password(password):
        abort(401, description='invalid credentials')
    eff = compute_effective_permissions(user.id)
    branch_ids = compute_branch_ids(user.id)
    claims = {
        'roles': eff['roles'],
        'perms': eff['perms'],
        'groups': eff['groups'],
    'branch_ids': branch_ids,
        'locale': user.locale
    }
    # JWT identity must be a string (flask-jwt-extended v4 requirement)
    token = create_access_token(identity=str(user.id), additional_claims=claims)
    return {'access_token': token}


@iam_bp.get('/auth/me')
@jwt_required()
def me():
    # Identity stored as string, cast back to int for DB lookup
    user_id = int(get_jwt_identity())
    session = get_db()
    user = session.execute(select(User).where(User.id==user_id)).scalar_one_or_none()
    if not user:
        abort(404)
    eff = compute_effective_permissions(user.id)
    branch_ids = compute_branch_ids(user.id)
    return {
        'id': user.id,
        'name': user.name,
        'email': user.email,
        'roles': eff['roles'],
        'perms': eff['perms'],
        'groups': eff['groups'],
        'locale': user.locale,
        'branch_ids': branch_ids
    }


# --- Group Management ---

@iam_bp.get('/groups')
@require_permissions('ADMIN.GROUP.MANAGE')
def list_groups():
    session = get_db()
    q = session.query(Group)
    try:
        limit, offset = normalize_pagination(request.args.get('limit'), request.args.get('offset'))
    except ValueError as e:
        abort(400, description=str(e))
    total = q.count()
    rows = q.order_by(Group.id.asc()).offset(offset).limit(limit).all()
    payload = {
        'data': [
            {
                'id': g.id,
                'name': g.name,
                'roles': [gr.role.name for gr in g.roles],
                'branch_scope': g.branch_scope or {}
            } for g in rows
        ],
        'pagination': {
            'total': total,
            'limit': limit,
            'offset': offset,
            'returned': len(rows)
        }
    }
    latest_ts = rows[0].updated_at if rows else None
    resp, etag = make_cached_list_response(payload['data'], total, limit, offset, latest_ts)
    cond = handle_conditional(etag, latest_ts)
    if cond:
        return cond
    return resp

@iam_bp.route('/groups', methods=['HEAD'])
@require_permissions('ADMIN.GROUP.MANAGE')
def head_groups():
    session = get_db()
    q = session.query(Group)
    try:
        limit, offset = normalize_pagination(request.args.get('limit'), request.args.get('offset'))
    except ValueError as e:
        abort(400, description=str(e))
    total = q.count()
    rows = q.order_by(Group.id.asc()).offset(offset).limit(limit).all()
    latest_ts = rows[0].updated_at if rows else None
    data = [
        {'id': g.id, 'name': g.name, 'roles': [gr.role.name for gr in g.roles], 'branch_scope': g.branch_scope or {}}
        for g in rows
    ]
    resp, etag = make_cached_list_response(data, total, limit, offset, latest_ts)
    cond = handle_conditional(etag, latest_ts)
    if cond:
        cond.set_data(b'')
        return cond
    resp.set_data(b'')
    return resp


@iam_bp.post('/groups')
@require_permissions('ADMIN.GROUP.MANAGE')
@audit_log('GROUP.CREATE', entity='Group', entity_id_key='id', meta_keys=['name'])
def create_group():
    data = request.json or {}
    name = data.get('name')
    if not name:
        abort(400, description='name required')
    session = get_db()
    if session.execute(select(Group).where(Group.name==name)).scalar_one_or_none():
        abort(400, description='group exists')
    grp = Group(name=name, description_i18n=data.get('description_i18n') or {}, branch_scope=data.get('branch_scope'))
    session.add(grp)
    session.flush()  # to get id
    session.commit()
    return {'id': grp.id, 'name': grp.name}, 201


@iam_bp.put('/groups/<int:group_id>')
@require_permissions('ADMIN.GROUP.MANAGE')
@audit_log(
    'GROUP.UPDATE',
    entity='Group',
    entity_id_key='id',
    meta_keys=['name'],
    diff_keys=['name', 'branch_scope'],
    pre_fetch=lambda a, kw: _prefetch_group_update(kw.get('group_id')),
)
def update_group(group_id: int):
    session = get_db()
    grp = session.execute(select(Group).where(Group.id==group_id)).scalar_one_or_none()
    if not grp:
        abort(404)
    data = request.json or {}
    # Update simple fields
    if 'name' in data:
        new_name = data['name']
        if not new_name:
            abort(400, description='name cannot be empty')
        # uniqueness check
        existing = session.execute(select(Group).where(Group.name==new_name, Group.id!=grp.id)).scalar_one_or_none()
        if existing:
            abort(400, description='group name in use')
        grp.name = new_name
    if 'description_i18n' in data:
        grp.description_i18n = data['description_i18n'] or {}
    if 'branch_scope' in data:
        scope = data['branch_scope']
        if scope is not None and not isinstance(scope, dict):
            abort(400, description='branch_scope must be object with optional allow array')
        # light validation: ensure allow is list of ints if present
        allow = scope.get('allow') if scope else None
        if allow is not None and (not isinstance(allow, list) or any(not isinstance(x, int) for x in allow)):
            abort(400, description='branch_scope.allow must be list[int]')
        grp.branch_scope = scope
    session.commit()
    return {'id': grp.id, 'name': grp.name, 'branch_scope': grp.branch_scope or {}}


def _prefetch_group_update(group_id: int):  # helper for audit decorator pre_fetch
    from app import get_db
    from sqlalchemy import select
    from app.models.authz import Group
    session = get_db()
    grp = session.execute(select(Group).where(Group.id==group_id)).scalar_one_or_none()
    if not grp:
        return {}
    return {'name': grp.name, 'branch_scope': grp.branch_scope or {}}


@iam_bp.delete('/groups/<int:group_id>')
@require_permissions('ADMIN.GROUP.MANAGE')
def delete_group(group_id: int):
    session = get_db()
    grp = session.execute(select(Group).where(Group.id==group_id)).scalar_one_or_none()
    if not grp:
        abort(404)
    session.delete(grp)
    add_audit('GROUP.DELETE', 'Group', group_id, {'name': grp.name})
    session.commit()
    return {'status': 'deleted'}


@iam_bp.put('/groups/<int:group_id>/roles')
@require_permissions('ADMIN.GROUP.MANAGE')
@audit_log('GROUP.ROLES.SET', entity='Group', entity_id_key='group_id', meta_keys=['role_ids'])
def set_group_roles(group_id: int):
    session = get_db()
    grp = session.execute(select(Group).where(Group.id==group_id)).scalar_one_or_none()
    if not grp:
        abort(404)
    data = request.json or {}
    role_ids = set(data.get('role_ids') or [])
    roles = session.execute(select(Role).where(Role.id.in_(list(role_ids)))).scalars().all() if role_ids else []
    existing_ids = {r.id for r in roles}
    missing = role_ids - existing_ids
    if missing:
        abort(400, description=f'Unknown role ids: {sorted(missing)}')
    # Replace
    session.execute(delete(GroupRole).where(GroupRole.group_id==grp.id))
    for rid in role_ids:
        session.add(GroupRole(group_id=grp.id, role_id=rid))
    session.commit()
    return {'group_id': grp.id, 'role_ids': sorted(role_ids)}


@iam_bp.put('/users/<int:user_id>/groups')
@require_permissions('ADMIN.USER.MANAGE')
@audit_log('USER.GROUPS.SET', entity='User', entity_id_key='user_id', meta_keys=['group_ids'])
def set_user_groups(user_id: int):
    session = get_db()
    user = session.execute(select(User).where(User.id==user_id)).scalar_one_or_none()
    if not user:
        abort(404)
    data = request.json or {}
    group_ids = set(data.get('group_ids') or [])
    groups = session.execute(select(Group).where(Group.id.in_(list(group_ids)))).scalars().all() if group_ids else []
    existing_ids = {g.id for g in groups}
    missing = group_ids - existing_ids
    if missing:
        abort(400, description=f'Unknown group ids: {sorted(missing)}')
    # Replace assignments
    session.execute(delete(UserGroup).where(UserGroup.user_id==user.id))
    for gid in group_ids:
        session.add(UserGroup(user_id=user.id, group_id=gid))
    session.commit()
    return {'user_id': user.id, 'group_ids': sorted(group_ids)}


# --- Audit Log Listing ---
@iam_bp.get('/audit/logs')
@require_permissions('ADMIN.SETTINGS.MANAGE')
def list_audit_logs():
    session = get_db()
    # Filters
    q = session.query(AuditLog)
    actor = request.args.get('actor_user_id')
    action = request.args.get('action')
    entity = request.args.get('entity')
    entity_id = request.args.get('entity_id')
    if actor:
        try:
            q = q.filter(AuditLog.actor_user_id==int(actor))
        except ValueError:
            abort(400, description='actor_user_id must be int')
    if action:
        q = q.filter(AuditLog.action==action)
    if entity:
        q = q.filter(AuditLog.entity==entity)
    if entity_id:
        q = q.filter(AuditLog.entity_id==entity_id)
    # Simple pagination
    try:
        limit = int(request.args.get('limit', 50))
        offset = int(request.args.get('offset', 0))
    except ValueError:
        abort(400, description='limit/offset must be int')
    limit = max(1, min(limit, 200))
    total = q.count()
    rows = q.order_by(AuditLog.id.desc()).offset(offset).limit(limit).all()
    payload = {
        'data': [
            {
                'id': r.id,
                'actor_user_id': r.actor_user_id,
                'action': r.action,
                'entity': r.entity,
                'entity_id': r.entity_id,
                'meta': r.meta,
                'created_at': r.created_at.isoformat() if r.created_at else None
            } for r in rows
        ],
        'pagination': {
            'total': total,
            'limit': limit,
            'offset': offset,
            'returned': len(rows)
        }
    }
    # ETag seed includes ids sequence + top record timestamp (most recent) for quick invalidation when new logs arrive
    latest_ts = rows[0].created_at if rows else None
    resp, etag = make_cached_list_response(payload['data'], total, limit, offset, latest_ts)
    cond = handle_conditional(etag, latest_ts)
    if cond:
        return cond
    return resp

@iam_bp.route('/audit/logs', methods=['HEAD'])
@require_permissions('ADMIN.SETTINGS.MANAGE')
def head_audit_logs():
    session = get_db()
    q = session.query(AuditLog)
    actor = request.args.get('actor_user_id'); action = request.args.get('action'); entity = request.args.get('entity'); entity_id = request.args.get('entity_id')
    if actor:
        try:
            q = q.filter(AuditLog.actor_user_id==int(actor))
        except ValueError:
            abort(400, description='actor_user_id must be int')
    if action:
        q = q.filter(AuditLog.action==action)
    if entity:
        q = q.filter(AuditLog.entity==entity)
    if entity_id:
        q = q.filter(AuditLog.entity_id==entity_id)
    try:
        limit = int(request.args.get('limit', 50)); offset = int(request.args.get('offset', 0))
    except ValueError:
        abort(400, description='limit/offset must be int')
    limit = max(1, min(limit, 200))
    total = q.count()
    rows = q.order_by(AuditLog.id.desc()).offset(offset).limit(limit).all()
    latest_ts = rows[0].created_at if rows else None
    data = [
        {'id': r.id, 'actor_user_id': r.actor_user_id, 'action': r.action, 'entity': r.entity, 'entity_id': r.entity_id, 'meta': r.meta, 'created_at': r.created_at.isoformat() if r.created_at else None}
        for r in rows
    ]
    resp, etag = make_cached_list_response(data, total, limit, offset, latest_ts)
    cond = handle_conditional(etag, latest_ts)
    if cond:
        cond.set_data(b'')
        return cond
    resp.set_data(b'')
    return resp
