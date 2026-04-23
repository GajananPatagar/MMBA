import re, time
from typing import Dict, Any, Optional

class VisionModule:
    def __init__(self, bus, memory):
        self.bus = bus
        self.memory = memory
        self._scan_count = 0
        self._last_frame = None

    def start(self):
        pass

    def analyze(self, text):
        result = {
            "raw_input": text,
            "tokens": re.findall(r'\b\w+\b', text.lower()),
            "intent": self._detect_intent(text),
            "entities": self._extract_entities(text),
            "timestamp": time.time(),
        }
        self._last_frame = result
        self.memory.store("vision:last_frame", result)
        return result

    def _detect_intent(self, text):
        t = text.lower()
        if any(w in t for w in ["create","build","make","generate","write"]):
            return "CREATE"
        if any(w in t for w in ["click","press","open","run","execute"]):
            return "ACTION"
        if any(w in t for w in ["find","search","locate","show"]):
            return "SEARCH"
        if any(w in t for w in ["analyze","check","inspect"]):
            return "ANALYZE"
        return "GENERAL"

    def _extract_entities(self, text):
        return {
            "files": re.findall(r'\b[\w\-]+\.\w{2,4}\b', text),
            "paths": re.findall(r'[/~][\w/\-\.]+', text),
            "numbers": re.findall(r'\b\d+\b', text),
        }

    def get_status(self):
        return f"scans={self._scan_count} | last={'yes' if self._last_frame else 'no'}"
