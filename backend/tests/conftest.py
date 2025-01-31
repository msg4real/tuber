from werkzeug.test import Client
import importlib
import fakeredis
import pytest
import sys
import os

def csrf(client):
    for cookie in client.cookie_jar:
        if cookie.name == "csrf_token":
            return cookie.value
    return ""

@pytest.fixture(params=[True, False])
def tuber(redis=False):
    os.environ['FORCE_HTTPS'] = "false"
    os.environ['FLASK_ENV'] = "development"
    os.environ['REDIS_URL'] = ""
    os.environ['DATABASE_URL'] = "sqlite:///test.db"
    os.environ['CIRCUITBREAKER_TIMEOUT'] = "5"
    os.environ['ENABLE_CIRCUITBREAKER'] = "true"
    mod = importlib.import_module('tuber')
    tuber.backgroundjobs = importlib.import_module('tuber.backgroundjobs')
    settings_override = {
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': "sqlite:///test.db"
    }
    mod.app.config.update(settings_override)
    if redis:
        redis = fakeredis.FakeStrictRedis()
        mod.db.r = redis
    yield mod
    for key in list(sys.modules.keys()):
        if key.startswith("tuber"):
            del sys.modules[key]

@pytest.fixture
def client_fresh(tuber):
    """Creates a client with a fresh database and no active sessions. Initial setup will not yet be completed.
    """
    tuber.database.create_tables()
    if os.environ['ENABLE_CIRCUITBREAKER'].lower() == "true":
        yield Client(tuber.backgroundjobs.AsyncMiddleware(tuber.app))
    else:
        with tuber.app.test_client() as client:
            yield client
    tuber.database.drop_tables()
    del sys.modules['tuber']

@pytest.fixture
def client(tuber):
    """Creates a test client with initial setup complete and the admin user logged in already.
    Also patches the get/post/patch/delete functions to handle CSRF tokens for you.
    """
    tuber.database.create_tables()
    if os.environ['ENABLE_CIRCUITBREAKER'].lower() == "true":
        client = Client(tuber.backgroundjobs.AsyncMiddleware(tuber.app))
    else:
        client = tuber.app.test_client()
    #with tuber.app.test_client() as client:
    #client = Client(tuber.backgroundjobs.AsyncMiddleware(tuber.app))
    client.post('/api/initial_setup', json={"username": "admin", "email": "admin@magfest.org", "password": "admin"})
    client.post("/api/login", json={"username": "admin", "password": "admin"}, headers={"CSRF-Token": csrf(client)})
    client.post("/api/event", json={"name": "Tuber Event", "description": "It's a potato"}, headers={"CSRF-Token": csrf(client)})
    _get = client.get
    def get(*args, **kwargs):
        if not 'headers' in kwargs:
            kwargs['headers'] = {}
        kwargs['headers']['CSRF-Token'] = csrf(client)
        rv = _get(*args, **kwargs)
        return rv
    _post = client.post
    def post(*args, **kwargs):
        if not 'headers' in kwargs:
            kwargs['headers'] = {}
        kwargs['headers']['CSRF-Token'] = csrf(client)
        rv = _post(*args, **kwargs)
        return rv
    _patch = client.patch
    def patch(*args, **kwargs):
        if not 'headers' in kwargs:
            kwargs['headers'] = {}
        kwargs['headers']['CSRF-Token'] = csrf(client)
        rv = _patch(*args, **kwargs)
        return rv
    _delete = client.delete
    def delete(*args, **kwargs):
        if not 'headers' in kwargs:
            kwargs['headers'] = {}
        kwargs['headers']['CSRF-Token'] = csrf(client)
        rv = _delete(*args, **kwargs)
        return rv
    client.get = get
    client.post = post
    client.patch = patch
    client.delete = delete
    yield client
    tuber.database.drop_tables()

@pytest.fixture
def prod_client():
    os.environ['REDIS_URL'] = ""
    os.environ['DATABASE_URL'] = "sqlite:///test.db"
    os.environ['CIRCUITBREAKER_TIMEOUT'] = "5"
    os.environ['FORCE_HTTPS'] = "true"
    os.environ['FLASK_ENV'] = "production"
    tuber = importlib.import_module('tuber')
    tuber.backgroundjobs = importlib.import_module('tuber.backgroundjobs')
    tuber.database.create_tables()
    if os.environ['ENABLE_CIRCUITBREAKER'].lower() == "true":
        yield Client(tuber.backgroundjobs.AsyncMiddleware(tuber.app))
    else:
        with tuber.app.test_client() as client:
            yield client
    tuber.database.drop_tables()
    for key in list(sys.modules.keys()):
        if key.startswith("tuber"):
            del sys.modules[key]