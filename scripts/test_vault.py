"""Demo for `VajraBackend.vault`.

Creates a vault, stores a sample file, retrieves it, and prints the audit trail.
"""
from __future__ import annotations

import os
from VajraBackend.vault import VaultManager


def demo():
    # optionally set VAJRA_MASTER_KEY env to a persistent base64 key
    vm = VaultManager()
    print("Vault root:", vm.root)
    name = "tier1-sensitive"
    vm.create_vault(name, tier=1)
    content = b"secret payload: do not share"
    vm.store_object(name, content, "secret.bin", actor="operator1")
    objs = vm.list_objects(name)
    print("objects:", objs)
    data = vm.retrieve_object(name, "secret.bin", actor="operator1")
    print("retrieved:", data)
    print("audit:")
    for e in vm.audit(name):
        print(e)


if __name__ == "__main__":
    demo()
