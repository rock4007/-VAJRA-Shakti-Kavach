#!/usr/bin/env python3
"""Example heartbeat sender that signs payload with HMAC secret and POSTs to /api/heartbeat.

Usage:
  VAJRA_SECRET_TESTCLIENT=mysupersecret python scripts/send_heartbeat.py --actor TESTCLIENT --device demo --hr 78 --url http://localhost:8008
"""
import os
import sys
import json
import time
import argparse
import uuid
import hmac
import hashlib
import requests

from datetime import datetime


def sign(secret: str, message: bytes) -> str:
    return hmac.new(secret.encode('utf-8'), message, hashlib.sha256).hexdigest()


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--actor', required=True)
    p.add_argument('--device', default='demo')
    p.add_argument('--hr', type=float, default=72.0)
    p.add_argument('--url', default='http://localhost:8008')
    args = p.parse_args()

    secret_env = f'VAJRA_SECRET_{args.actor.upper()}'
    secret = os.environ.get(secret_env)
    if not secret:
        print('Missing secret env var:', secret_env)
        sys.exit(2)

    payload = {
        'device': args.device,
        'hr': args.hr,
        'ts': datetime.utcnow().isoformat()
    }
    body = json.dumps(payload).encode('utf-8')
    sig = sign(secret, body)
    nonce = str(uuid.uuid4())

    headers = {
        'Content-Type': 'application/json',
        'X-Actor': args.actor,
        'X-Nonce': nonce,
        'X-Signature': sig
    }

    resp = requests.post(args.url.rstrip('/') + '/api/heartbeat', data=body, headers=headers, timeout=5)
    print(resp.status_code, resp.text)


if __name__ == '__main__':
    main()
