import requests
import time

url = 'http://localhost:8009/heartrate/stream'
print(f'Connecting to {url}...')
try:
    with requests.get(url, stream=True, timeout=10) as r:
        r.raise_for_status()
        start = time.time()
        for line in r.iter_lines(decode_unicode=True):
            if line:
                print(line)
            # stop after ~8 seconds
            if time.time() - start > 8:
                break
except Exception as e:
    print('SSE stream failed:', e)

print('SSE test complete')
