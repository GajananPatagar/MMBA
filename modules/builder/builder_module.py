import os, json, time, hashlib
from datetime import datetime
from typing import Dict, List, Any

MAP_PATH  = "./data/knowledge_map.json"
PAT_PATH  = "./data/learned_patterns.json"

class KnowledgeEntry:
    def __init__(self, command, outcome, success):
        self.command   = command
        self.outcome   = str(outcome)
        self.success   = success
        self.timestamp = datetime.now().isoformat()
        self.id        = hashlib.md5(
            f"{command}{self.timestamp}".encode()
        ).hexdigest()[:10]

    def to_dict(self):
        return {
            "id":        self.id,
            "command":   self.command,
            "outcome":   self.outcome,
            "success":   self.success,
            "timestamp": self.timestamp,
        }

class BuilderModule:
    def __init__(self, bus, memory):
        self.bus      = bus
        self.memory   = memory
        self._map     = []
        self._patterns = {}
        self._observe_count = 0
        self._improve_count = 0
        os.makedirs("./data", exist_ok=True)
        self._load()

    def start(self):
        pass

    def learn(self, command, outcome):
        success = self._assess(outcome)
        entry   = KnowledgeEntry(command, outcome, success)
        self._map.append(entry)
        self._observe_count += 1
        if success:
            self._extract_pattern(command)
        if self._observe_count % 5 == 0:
            self._save()
        print(f"  [BUILD] Learned: '{command[:30]}' → {'✓' if success else '✗'}")
        return entry

    def _assess(self, outcome):
        if outcome is None:
            return False
        bad = ["error","failed","exception","blocked","✗"]
        return not any(b in str(outcome).lower() for b in bad)

    def _extract_pattern(self, command):
        cmd = command.lower()
        key = None
        if "git" in cmd:
            key = "git_workflow"
        elif "python" in cmd:
            key = "python_exec"
        elif "create" in cmd or "build" in cmd:
            key = "creation_task"
        if key:
            p = self._patterns.get(key, {"count": 0})
            p["count"] += 1
            p["last"] = command
            self._patterns[key] = p

    def run_training_loop(self, iterations=3):
        print(f"[BUILD] Training ({iterations} iterations)...")
        for i in range(iterations):
            print(f"\n  Iteration {i+1}/{iterations}")
            total   = len(self._map)
            success = sum(1 for e in self._map if e.success)
            rate    = (success/total*100) if total else 0
            print(f"  Observations : {total}")
            print(f"  Success rate : {rate:.1f}%")
            print(f"  Patterns     : {list(self._patterns.keys())}")
            self._improve_count += 1
            time.sleep(0.5)
        self._save()
        print(f"\n[BUILD] Training done. {self._improve_count} improvements.")

    def _save(self):
        try:
            with open(MAP_PATH, "w") as f:
                json.dump([e.to_dict() for e in self._map], f, indent=2)
            with open(PAT_PATH, "w") as f:
                json.dump(self._patterns, f, indent=2)
        except Exception as e:
            print(f"  [BUILD] Save error: {e}")

    def _load(self):
        try:
            if os.path.exists(MAP_PATH):
                with open(MAP_PATH) as f:
                    for item in json.load(f):
                        e = KnowledgeEntry(
                            item["command"],
                            item["outcome"],
                            item["success"]
                        )
                        self._map.append(e)
                print(f"  [BUILD] Loaded {len(self._map)} entries.")
            if os.path.exists(PAT_PATH):
                with open(PAT_PATH) as f:
                    self._patterns = json.load(f)
        except:
            pass

    def get_status(self):
        return (f"observed={self._observe_count} | "
                f"improved={self._improve_count} | "
                f"patterns={len(self._patterns)} | "
                f"map={len(self._map)}")
