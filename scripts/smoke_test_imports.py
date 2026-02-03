#!/usr/bin/env python3
"""Smoke test: verify security packages import correctly."""
import sys
def try_import(name, expr):
    try:
        mod = __import__(expr)
        ver = getattr(mod, '__version__', 'unknown')
        print('IMPORT_OK', name, ver)
        return True
    except Exception as e:
        print('IMPORT_FAIL', name, str(e))
        return False

ok = True
ok &= try_import('flask_talisman', 'flask_talisman')
ok &= try_import('flask_limiter', 'flask_limiter')
ok &= try_import('cryptography', 'cryptography')
ok &= try_import('redis', 'redis')
sys.exit(0 if ok else 2)
