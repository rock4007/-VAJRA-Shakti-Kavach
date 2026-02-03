# Tiny verification harness for Redis-backed admin SSE generator
# This script mocks a Redis client and exercises the admin_events SSE generator
import json
import time
import threading

# Import the Flask app and admin_events from the backend
import os, sys, importlib.util

# Load the backend module by path to avoid package import issues
backend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'VajraBackend', 'main.py'))
spec = importlib.util.spec_from_file_location('vajra_main', backend_path)
main = importlib.util.module_from_spec(spec)
spec.loader.exec_module(main)

class MockPubSub:
    def __init__(self):
        self.messages = []
        self._closed = False

    def subscribe(self, channel):
        self.channel = channel

    def get_message(self, timeout=1.0):
        # Return a queued message if available, otherwise wait for timeout
        if self.messages:
            m = self.messages.pop(0)
            return {'type': 'message', 'data': json.dumps(m)}
        # sleep a short time instead of blocking full timeout
        time.sleep(0.05)
        return None

    def unsubscribe(self, channel):
        pass

    def close(self):
        self._closed = True

class MockRedis:
    def __init__(self, pubsub):
        self._pubsub = pubsub

    def pubsub(self):
        return self._pubsub

    def publish(self, channel, data):
        try:
            self._pubsub.messages.append(json.loads(data))
            return 1
        except Exception:
            return 0


def run_test():
    # Arrange: install a MockRedis into main
    pubsub = MockPubSub()
    mock_redis = MockRedis(pubsub)
    main.REDIS_CLIENT = mock_redis

    # Prepare a test payload
    test_payload = {
        'type': 'sos_alert',
        'ts': time.strftime('%Y-%m-%dT%H:%M:%S'),
        'device_id': 'TEST_DEVICE',
        'lat': 12.34,
        'lon': 56.78,
        'maps_link': 'https://maps.test/',
        'distress': True
    }

    # Act: publish the payload
    mock_redis.publish('vajra:admin_events', json.dumps(test_payload))

    # Create a Flask test request context and call the admin_events endpoint
    app = main.app
    with app.test_request_context('/admin/events'):
        resp = main.admin_events()
        # resp is a Response object; its iterable is resp.response
        it = resp.response
        # Read several yielded chunks
        outputs = []
        try:
            for i, chunk in enumerate(it):
                s = chunk.decode() if isinstance(chunk, (bytes, bytearray)) else str(chunk)
                s = s.strip()
                if not s:
                    continue
                outputs.append(s)
                # Stop after we've seen the test_payload content
                if 'sos_alert' in s or 'TEST_DEVICE' in s:
                    break
                if i > 10:
                    break
        except GeneratorExit:
            pass

    print('\n--- SSE generator output chunks ---')
    for o in outputs:
        print(o)

    # Basic assertion
    matched = any('TEST_DEVICE' in o or 'sos_alert' in o for o in outputs)
    print('\nTest result:', 'PASS' if matched else 'FAIL')

if __name__ == '__main__':
    run_test()
