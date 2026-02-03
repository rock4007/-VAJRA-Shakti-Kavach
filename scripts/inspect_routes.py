#!/usr/bin/env python3
import importlib.util, os
p = os.path.abspath('VajraBackend/main.py')
spec = importlib.util.spec_from_file_location('vajra_main', p)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
app = getattr(mod, 'app')
print('Registered routes:')
for rule in app.url_map.iter_rules():
    print(str(rule))
