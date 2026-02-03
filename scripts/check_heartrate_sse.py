#!/usr/bin/env python3
"""Connect to /heartrate/stream and print a few parsed BPM samples."""
import requests
import sys
import time

URL = 'http://127.0.0.1:8009/heartrate/stream'
try:
    with requests.get(URL, stream=True, timeout=10) as r:
        if r.status_code != 200:
            print('STREAM_STATUS', r.status_code)
            sys.exit(2)
        print('Connected to SSE stream, reading 6 samples...')
        buf = ''
        samples = 0
        start = time.time()
        for line in r.iter_lines(chunk_size=1, decode_unicode=True):
            if line is None:
                continue
            if line.strip() == '':
                # event boundary
                if buf.startswith('data:'):
                    payload = buf[len('data:'):].strip()
                    try:
                        import json
                        obj = json.loads(payload)
                        print('EVENT:', obj)
                        samples += 1
                        if samples >= 6:
                            break
                    except Exception as e:
                        print('PARSE_ERR', e, payload)
                buf = ''
            else:
                buf += (line + '\n')
            if time.time() - start > 20:
                print('TIMEOUT waiting for samples')
                break
except Exception as e:
    print('ERROR:', e)
    sys.exit(1)

print('Done')
