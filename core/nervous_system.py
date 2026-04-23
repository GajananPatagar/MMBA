import time
from typing import Dict, Any

class NervousSystem:
    def __init__(self, bus, memory, settings):
        self.bus = bus
        self.memory = memory
        self.settings = settings
        self.modules = {}
        self._running = False
        self._command_history = []

    def register(self, name, module):
        self.modules[name] = module
        self.bus.register_module(name)
        if hasattr(module, "start"):
            module.start()
        print(f"  [NS] Module '{name}' connected ✓")

    def execute_command(self, command):
        print(f"\n[NS] Command: '{command}'")
        self._command_history.append(command)
        self.bus.send("ns", "vision", "ANALYZE", {"input": command})
        time.sleep(0.3)
        self.bus.send("ns", "logic", "REASON", {"command": command})
        time.sleep(0.3)
        self.bus.send("ns", "action", "EXECUTE", {"plan": command})
        time.sleep(0.3)
        self.bus.send("ns", "builder", "LEARN", {"command": command})
        return f"Command '{command}' processed."

    def run_autonomous(self):
        self._running = True
        print("[NS] Autonomous mode. Ctrl+C to stop.")
        try:
            while self._running:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n[NS] Stopped.")

    def interactive_shell(self):
        print("[NS] Interactive shell. Type 'exit' to quit.\n")
        while True:
            try:
                cmd = input("MMBA> ").strip()
                if cmd.lower() in ("exit", "quit"):
                    break
                elif cmd.lower() == "status":
                    self.print_status()
                elif cmd:
                    print(self.execute_command(cmd))
            except (KeyboardInterrupt, EOFError):
                break

    def print_status(self):
        mem = self.memory.usage_report()
        print("=" * 50)
        print("  MMBA SYSTEM STATUS")
        print("=" * 50)
        print(f"  Modules : {list(self.modules.keys())}")
        print(f"  RAM     : {mem['used_mb']}MB / {mem['limit_mb']}MB")
        print(f"  Status  : {mem['status']}")
        print(f"  Commands: {len(self._command_history)}")
        print("=" * 50)
        for name, mod in self.modules.items():
            s = mod.get_status() if hasattr(mod, "get_status") else "active"
            print(f"  [{name.upper():8s}] {s}")
        print("=" * 50)
