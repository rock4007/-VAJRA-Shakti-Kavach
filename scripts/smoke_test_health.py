#!/usr/bin/env python3
"""Smoke test: import the Flask app and GET /health via test client."""
import sys
import traceback
import os

try:
    # Load the Flask app module by path to avoid package import issues
    import importlib.util

    main_path = os.path.join(os.path.dirname(__file__), '..', 'VajraBackend', 'main.py')
    main_path = os.path.abspath(main_path)
    spec = importlib.util.spec_from_file_location('vajra_main', main_path)
    appmod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(appmod)

    app = getattr(appmod, 'app', None)
    if app is None:
        print("ERROR: 'app' not found in VajraBackend/main.py")
        sys.exit(2)

    client = app.test_client()
    resp = client.get('/health')
    print('STATUS_CODE:', resp.status_code)
    print('BODY:', resp.get_data(as_text=True))
    sys.exit(0 if resp.status_code == 200 else 3)
except Exception as e:
    print('EXCEPTION:', e)
    traceback.print_exc()
    sys.exit(1)
