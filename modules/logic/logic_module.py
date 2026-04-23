import os, json, time, hashlib
from typing import Any, Dict, Optional, List

KNOWLEDGE = {
    "GIT": {
        "push": "git add . && git commit -m 'update' && git push",
        "init": "git init && git branch -M main",
    },
    "TERMUX": {
        "setup": "pkg install python git openssh",
        "run": "python main.py",
    },
    "PLC": {
        "ladder": "NO contact → NC contact → Output coil",
        "timer": "TON=On-delay, TOF=Off-delay",
        "counter": "CTU=Count up, CTD=Count down",
    },
    "PYTHON": {
        "pattern": "Separate concerns into modules",
        "memory": "Use generators and chunked reading",
    },
}

class LogicModule:
    def __init__(self, bus, memory, brain_path):
        self.bus = bus
        self.memory = memory
        self.brain_path = brain_path
        self._reflex_cache = {}
        self._reason_count = 0
        self._reflex_count = 0
        print(f"  [LOGIC] Brain path: {brain_path}")

    def reason(self, command, context=None):
        reflex = self._reflex_lookup(command)
        if reflex:
            self._reflex_count += 1
            return {
                "mode": "reflex",
                "plan": reflex,
                "steps": [reflex],
            }
        self._reason_count += 1
        plan = self._deep_reason(command, context)
        self._reflex_cache[command.lower()] = plan
        return {
            "mode": "conscious",
            "plan": plan,
            "steps": plan.split(" | "),
        }

    def _reflex_lookup(self, command):
        cmd = command.lower()
        if cmd in self._reflex_cache:
            return self._reflex_cache[cmd]
        if "git push" in cmd or "push to github" in cmd:
            return KNOWLEDGE["GIT"]["push"]
        if "termux setup" in cmd:
            return KNOWLEDGE["TERMUX"]["setup"]
        if "ladder" in cmd and "create" in cmd:
            return KNOWLEDGE["PLC"]["ladder"]
        return None

    def _deep_reason(self, command, context=None):
        cmd = command.lower()
        parts = []
        if "create" in cmd or "build" in cmd:
            parts.append(f"Planning: {command}")
            parts.append("Use modular Python structure")
            parts.append("Separate each concern into files")
        elif "git" in cmd:
            parts.append(f"Git operation: {command}")
            parts.append(KNOWLEDGE["GIT"]["push"])
        elif "plc" in cmd or "ladder" in cmd:
            parts.append(f"PLC task: {command}")
            parts.append(KNOWLEDGE["PLC"]["ladder"])
        else:
            parts.append(f"Processing: {command}")
            parts.append("Analyze → Plan → Execute → Learn")
        return " | ".join(parts)

    def query(self, domain, key=None):
        d = KNOWLEDGE.get(domain.upper(), {})
        return d.get(key, d) if key else d

    def get_status(self):
        return (f"conscious={self._reason_count} | "
                f"reflex={self._reflex_count} | "
                f"cache={len(self._reflex_cache)}")
