import time
import json
import os
import importlib.util

# Load app
backend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'VajraBackend', 'main.py'))
spec = importlib.util.spec_from_file_location('vajra_main', backend_path)
main = importlib.util.module_from_spec(spec)
spec.loader.exec_module(main)
app = main.app


def test_sos_creates_alert_and_case():
    client = app.test_client()

    # Ensure no alerts yet
    r = client.get('/admin/alerts')
    assert r.status_code == 200
    assert r.get_json()['total'] == 0

    # Post SOS alert (distress true)
    payload = {
        'device_id': 'TEST_DEVICE_1',
        'lat': 12.34,
        'lon': 56.78,
        'distress': True,
        'ts': time.strftime('%Y-%m-%dT%H:%M:%S')
    }
    r = client.post('/sos_alert', json=payload)
    assert r.status_code == 200
    jr = r.get_json()
    assert jr['status'] == 'accepted'

    # Wait a short time for background dispatch thread to create case
    time.sleep(0.5)

    r2 = client.get('/admin/alerts')
    assert r2.status_code == 200
    data = r2.get_json()
    assert data['total'] >= 1
    # retrieve a case_id from internal state
    any_alerts = data['alerts']
    if any_alerts:
        cid = any_alerts[0]['case_id']
        # Acknowledge the alert
        ra = client.post(f'/admin/alerts/{cid}/ack', json={'admin_id': 'tester'})
        assert ra.status_code == 200
        ja = ra.get_json()
        assert ja['status'] == 'acknowledged'
        # Create case
        rc = client.post(f'/admin/alerts/{cid}/case', json={'admin_id': 'tester', 'notes': 'Test case'})
        assert rc.status_code == 200
        jc = rc.get_json()
        assert jc['status'] == 'case_created'


def test_admin_sse_inmemory_generator():
    # Ensure REDIS_CLIENT is None to exercise in-memory path
    main.REDIS_CLIENT = None
    with app.test_request_context('/admin/events'):
        resp = main.admin_events()
        it = resp.response
        # read first chunk (heartbeat)
        first = next(iter(it))
        s = first.decode() if isinstance(first, (bytes, bytearray)) else str(first)
        assert 'connected' in s


def test_drone_endpoints():
    client = app.test_client()
    # deploy
    payload = {'name': 'TestDrone', 'mission': 'patrol', 'location': '12.34,56.78'}
    r = client.post('/admin/drone/deploy', json=payload)
    assert r.status_code == 200
    jd = r.get_json()
    assert jd['status'] == 'deployed'
    drone_id = jd['drone']['id']

    # status
    rs = client.get('/admin/drone/status')
    assert rs.status_code == 200
    sd = rs.get_json()
    assert any(d['id'] == drone_id for d in sd['drones'])

    # recall
    rr = client.post('/admin/drone/recall', json={'id': drone_id})
    assert rr.status_code == 200
    jr = rr.get_json()
    assert jr['status'] == 'recalled'
