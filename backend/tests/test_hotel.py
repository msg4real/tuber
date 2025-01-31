from unittest.mock import patch
import json
import time

@patch('tuber.api.users.requests.post')
def test_staffer_auth(mock_post, client):
    """Make sure the staffer login system is able to authenticate against uber"""
    results = [{"result": []}, {"result": ["234"]},{"result": [{"id": "234", "email": "test1@test.com", "assigned_depts_labels": [], "staffing": True, "badge_num": "", "badge_printed_name": "", "full_name": "", "first_name": "", "last_name": "", "legal_name": "", "ec_name": "", "ec_phone": "", "cellphone": ""}]}]
    mock_post.return_value.json = results.pop
    rv = client.post('/api/uber_login', json={"token": "234"})
    assert(rv.status_code == 200)

    from tuber.database import db
    from tuber.models import Badge
    badge = Badge(email="test@magfest.com", uber_id="123")
    db.add(badge)
    db.commit()

    results = [{"result": []}, {"result": ["123"]},{"result": [{"id": "123", "email": "test2@test.com", "assigned_depts_labels": [], "staffing": True, "badge_num": "", "badge_printed_name": "", "full_name": "", "first_name": "", "last_name": "", "legal_name": "", "ec_name": "", "ec_phone": "", "cellphone": ""}]}]
    mock_post.return_value.json = results.pop
    rv = client.post('/api/uber_login', json={"token": "123"})
    assert(rv.status_code == 200)

    results = [{"result": []}, {"result": ["234"]},{"result": [{"id": "456", "email": "test3@test.com", "assigned_depts_labels": [], "staffing": True, "badge_num": "", "badge_printed_name": "", "full_name": "", "first_name": "", "last_name": "", "legal_name": "", "ec_name": "", "ec_phone": "", "cellphone": ""}]}]
    mock_post.return_value.json = results.pop
    rv = client.post('/api/uber_login', json={"token": "456"})
    assert(rv.status_code != 200)

def test_statistics(client):
    rv = client.get("/api/event/1/hotel/statistics", query_string={"event": 1})
    assert rv.json['num_badges'] == 0
    assert rv.json['num_requests'] == 0
    for i in range(100):
        badge = client.post("/api/event/1/badge", json={
            "legal_name": "Test User {}".format(i)
        }).json
        assert(badge['legal_name'] == "Test User {}".format(i))
    rv = client.get("/api/event/1/hotel/statistics", query_string={"event": 1})
    assert rv.json['num_badges'] == 100
    assert rv.json['num_requests'] == 0

def test_all_requests(client):
    rv = client.get("/api/event/1/hotel/all_requests", query_string={"event": 1})
    assert not rv.json
    rv = client.post("/api/importer/mock", json={
        "event": 1,
        "attendees": 100,
        "departments": 10,
        "staffers": 100,
    })
    if rv.status_code == 202:
        jobid = rv.json['job']
        while rv.status_code == 202:
            rv = client.get(f"/api/job/{jobid}")
            time.sleep(0.2)
    assert rv.status_code == 200
    rv = client.get("/api/event/1/hotel/all_requests", query_string={"event": 1})
    assert rv.status_code == 200
    assert rv.json
    for id, badge in rv.json.items():
        assert 'antirequested_roommates' in badge
        assert 'departments' in badge
        assert 'first_name' in badge
        assert 'id' in badge
        assert 'justification' in badge
        assert 'last_name' in badge
        assert 'legal_name' in badge
        assert 'name' in badge
        assert 'noise_level' in badge
        assert 'notes' in badge
        assert 'prefer_department' in badge
        assert 'prefer_single_gender' in badge
        assert 'preferred_department' in badge
        assert 'preferred_gender' in badge
        assert 'requested_roommates' in badge
        assert 'room_nights' in badge
        assert 'sleep_time' in badge
        assert 'smoke_sensitive' in badge

def test_requests(client):
    rv = client.get("/api/event/1/hotel/requests", query_string={"event": 1})
    assert not rv.json
    rv = client.post("/api/importer/mock", json={
        "event": 1,
        "attendees": 100,
        "departments": 10,
        "staffers": 100,
    })
    if rv.status_code == 202:
        jobid = rv.json['job']
        while rv.status_code == 202:
            rv = client.get(f"/api/job/{jobid}")
            time.sleep(0.2)
    assert rv.status_code == 200
    rv = client.get("/api/event/1/hotel/requests", query_string={"event": 1})
    assert rv.status_code == 200
    assert rv.json
    for dept in rv.json:
        assert 'id' in dept
        assert 'name' in dept
        assert 'requests' in dept
        for request in dept['requests']:
            assert 'id' in request
            assert 'justification' in request
            assert 'name' in request
            assert 'room_nights' in request

#def test_approve(client):
#    pass
#def test_room_nights(client):
#    pass
#def test_hotel_room(client):
#    pass
#def test_room_night(client):
#    pass
#def test_room_block(client):
#    pass
#def test_request_complete(client):
#    pass
#def test_room_assignments(client):
#    pass

def test_hotel_badges(client):
    rv = client.get("/api/event/1/hotel/badge_names", query_string={"event": 1})
    assert rv.json == []
    for i in range(100):
        badge = client.post("/api/event/1/badge", json={
            "legal_name": "Test User {}".format(i)
        }).json
        assert(badge['legal_name'] == "Test User {}".format(i))
    rv = client.get("/api/event/1/hotel/badge_names", query_string={"event": 1})
    assert len(rv.json) == 100