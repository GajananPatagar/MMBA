import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.bus import VirtualBus
from core.memory_manager import MemoryManager

def test_bus():
    bus = VirtualBus()
    bus.register_module("test")
    bus.send("a", "test", "PING", {"data": 1})
    msg = bus.receive("test", timeout=1.0)
    assert msg is not None
    assert msg.payload["data"] == 1
    print("✓ Bus test passed")

def test_memory():
    mem = MemoryManager(limit_mb=512)
    mem.store("key1", "value1")
    assert mem.retrieve("key1") == "value1"
    print("✓ Memory test passed")

if __name__ == "__main__":
    test_bus()
    test_memory()
    print("\n✓ All tests passed!")
