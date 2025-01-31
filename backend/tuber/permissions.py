from tuber import app, config
from flask import g, request
from tuber.models import Permission, Grant, Role, Department, DepartmentPermission, DepartmentGrant, DepartmentRole, Session, User, Badge
from tuber.database import db
import datetime
import json

@app.url_value_preprocessor
def load_session(endpoint, values):
    g.user = None
    g.badge = None
    g.session = None
    g.event = None
    g.department = None
    g.perms = {
        "event": {},
        "department": {}
    }

    if request.method != "GET":
        if not request.json is None:
            g.data = dict(request.json)
        elif not request.form is None:
            g.data = dict(request.form)
    elif not request.args is None:
        g.data = dict(request.args)

    if not values:
        values = {}
    if 'event' in values:
        g.event = int(values['event'])
    if 'department' in values:
        g.department = int(values['department'])
    if 'session' in request.cookies:
        session = db.query(Session).filter(Session.secret == request.cookies.get('session')).one_or_none()
        if session:
            if datetime.datetime.now() < session.last_active + datetime.timedelta(seconds=config.session_duration):
                session.last_active = datetime.datetime.now()
                g.session = session
                g.user = db.query(User).filter(User.id == session.user).one_or_none()
                g.badge = db.query(Badge).filter(Badge.id == session.badge).one_or_none()
                if "event" in values and not g.badge and g.user:
                    g.badge = db.query(Badge).filter(Badge.user == g.user.id, Badge.event == values['event']).one_or_none()
                perms = json.loads(session.permissions)
                g.perms = {
                    "event": {int(k) if k != '*' else k: v for k, v in perms['event'].items()},
                    "department": {int(k) if k != '*' else k: {int(m) if m != '*' else m: n for m, n in v.items()} for k, v in perms['department'].items()}
                }
                db.add(session)
            else:
                db.delete(session)
            db.commit()

def flush_session_perms(user_id=None):
    if user_id:
        sessions = db.query(Session).filter(Session.user == user_id).all()
    else:
        sessions = db.query(Session).all()
    for session in sessions:
        perms = get_permissions(user_id=session.user)
        session.permissions=json.dumps(perms)
        db.add(session)
    db.commit()

def get_permissions(user=None):
    if not user and g.user:
        user = g.user.id
    perm_cache = {
        "event": {},
        "department": {}
    }
    if not user:
        return perm_cache

    perms = db.query(Permission, Grant, Role).filter(Grant.user == user, Grant.role == Role.id, Permission.role == Role.id).all()
    for permission, grant, role in perms:
        event = grant.event
        if event == None:
            event = "*"
        if not event in perm_cache['event']:
            perm_cache['event'][event] = []
        perm_cache['event'][event].append(permission.operation)

    perm_cache['department'] = {}
    dep_perms = db.query(Department, DepartmentPermission, DepartmentGrant, DepartmentRole).filter(DepartmentGrant.department == Department.id, DepartmentGrant.user == user, DepartmentGrant.role == DepartmentRole.id, DepartmentPermission.role == DepartmentRole.id).all()
    for department, permission, grant, role in dep_perms:
        department = grant.department
        if not department.event in perm_cache['department']:
            perm_cache['department'][department.event] = {}
        if not department in perm_cache['department'][department.event]:
            perm_cache['department'][department.event][department.id] = []
        perm_cache['department'][department.event][department.id].append(permission.operation)
    return perm_cache

def check_permission(permission=None, event="*", department="*"):
    if isinstance(permission, list):
        if len(permission) > 1:
            return check_permission(permission[0], event, department) or check_permission(permission[1:], event, department)
        permission = permission[0]
    req_table, req_instance, req_action = permission.split(".")
    for perm_event in g.perms['event']:
        for perm in g.perms['event'][perm_event]:
            table, instance, action = perm.split(".")
            if perm_event != "*" and perm_event != event:
                continue
            if table != "*" and table != req_table:
                continue
            if instance != "*" and instance != req_instance:
                continue
            if action != "*" and action != req_action:
                continue
            return True
    for perm_event in g.perms['department']:
        for perm_dept in g.perms['department'][perm_event]:
            for perm in g.perms['department'][perm_event][perm_dept]:
                table, instance, action = perm.split(".")
                if perm_event != "*" and perm_event != event:
                    continue
                if perm_dept != department:
                    continue
                if table != "*" and table != req_table:
                    continue
                if instance != "*" and instance != req_instance:
                    continue
                if action != "*" and action != req_action:
                    continue
                return True
    return False