import os, time, subprocess
from typing import Any, List

class ActionResult:
    def __init__(self, success, output, duration_ms=0):
        self.success = success
        self.output = output
        self.duration_ms = duration_ms

    def __repr__(self):
        s = "✓" if self.success else "✗"
        return f"[{s}] {self.output[:60]}"

class ActionModule:
    def __init__(self, bus, memory):
        self.bus = bus
        self.memory = memory
        self._history = []
        self._dry_run = False

    def start(self):
        pass

    def execute(self, plan):
        steps = plan.get("steps", [plan.get("plan", "")])
        outputs = []
        success = True
        for step in steps:
            r = self._execute_step(str(step))
            outputs.append(r.output)
            if not r.success:
                success = False
                break
        ar = ActionResult(success, " → ".join(outputs))
        self._history.append(ar)
        return ar

    def _execute_step(self, step):
        s = step.lower()
        if step.startswith("Execute:") or step.startswith("Run:"):
            cmd = step.split(":", 1)[1].strip()
            return self.run_shell(cmd)
        if "&&" in step or step.startswith("git") or step.startswith("pkg"):
            return self.run_shell(step)
        if "python" in s and ("print" in s or "import" in s):
            return self.run_python(step)
        return ActionResult(True, f"[plan] {step}")

    def run_shell(self, command, timeout=30):
        blocked = ["rm -rf /", ":(){:|:&};:"]
        for b in blocked:
            if b in command:
                return ActionResult(False, f"BLOCKED: {command}")
        try:
            start = time.time()
            r = subprocess.run(
                command, shell=True,
                capture_output=True, text=True, timeout=timeout
            )
            ms = (time.time() - start) * 1000
            out = (r.stdout or r.stderr or "").strip()
            print(f"  [ACT] {command[:40]} → {'OK' if r.returncode==0 else 'ERR'}")
            return ActionResult(r.returncode == 0, out[:300], ms)
        except subprocess.TimeoutExpired:
            return ActionResult(False, "Timeout", timeout*1000)
        except Exception as e:
            return ActionResult(False, str(e))

    def run_python(self, code, timeout=10):
        try:
            r = subprocess.run(
                ["python3", "-c", code],
                capture_output=True, text=True, timeout=timeout
            )
            return ActionResult(r.returncode==0,
                                (r.stdout or r.stderr).strip()[:300])
        except Exception as e:
            return ActionResult(False, str(e))

    def write_file(self, path, content):
        try:
            os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
            with open(path, "w") as f:
                f.write(content)
            return ActionResult(True, f"Written: {path}")
        except Exception as e:
            return ActionResult(False, str(e))

    def get_status(self):
        ok = sum(1 for r in self._history if r.success)
        return f"actions={len(self._history)} | success={ok}"
