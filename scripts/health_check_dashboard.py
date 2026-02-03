"""
Health check for admin dashboard endpoints and SSE generator.
Verifies: /admin/alerts (GET), /admin/alerts/<case_id>/ack (POST), /admin/alerts/<case_id>/case (POST), and admin_events SSE generator returns an iterable without crashing.
"""
import json
import os
import importlib.util
import time

# load main.py
backend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'VajraBackend', 'main.py'))
spec = importlib.util.spec_from_file_location('vajra_main', backend_path)
main = importlib.util.module_from_spec(spec)
spec.loader.exec_module(main)

app = main.app

results = []

# 1) GET /admin/alerts
try:
    with app.test_client() as c:
        r = c.get('/admin/alerts')
        results.append(('/admin/alerts', r.status_code, r.get_json()))
except Exception as e:
    results.append(('/admin/alerts', 'EXCEPTION', str(e)))

# 2) POST ack for fake case -> expect 404 but no crash
fake_case = 'nonexistent-case-123'
try:
    with app.test_client() as c:
        r = c.post(f'/admin/alerts/{fake_case}/ack', json={'admin_id': 'healthcheck'})
        try:
            j = r.get_json()
        except Exception:
            j = None
        results.append((f'/admin/alerts/{fake_case}/ack', r.status_code, j))
except Exception as e:
    results.append((f'/admin/alerts/{fake_case}/ack', 'EXCEPTION', str(e)))

# 3) POST create case for fake case -> expect 404 or error, but no crash
try:
    with app.test_client() as c:
        r = c.post(f'/admin/alerts/{fake_case}/case', json={'admin_id': 'healthcheck', 'notes': 'test'})
        try:
            j = r.get_json()
        except Exception:
            j = None
        results.append((f'/admin/alerts/{fake_case}/case', r.status_code, j))
except Exception as e:
    results.append((f'/admin/alerts/{fake_case}/case', 'EXCEPTION', str(e)))

# 4) Call admin_events generator to ensure it yields initial heartbeat and doesn't crash.
# We'll run it in a test_request_context and read a few chunks.
try:
    with app.test_request_context('/admin/events'):
        resp = main.admin_events()
        # resp.response is an iterator/generator
        it = resp.response
        chunks = []
        try:
            for i, chunk in enumerate(it):
                s = chunk.decode() if isinstance(chunk, (bytes, bytearray)) else str(chunk)
                s = s.strip()
                if s:
                    chunks.append(s)
                if i >= 3:
                    break
        except Exception as e:
            chunks.append('EXCEPTION:' + str(e))
        results.append(('/admin/events (generator)', 'ITERATED', chunks))
except Exception as e:
    results.append(('/admin/events (generator)', 'EXCEPTION', str(e)))

print('\n=== Admin Dashboard Health Check Results ===')
for r in results:
    print(r)

# Simple pass/fail
fail = any(x[1] == 'EXCEPTION' for x in results)
print('\nOverall:', 'PASS' if not fail else 'FAIL')
