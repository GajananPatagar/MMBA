"""
ModelRouter — Routes requests to correct AI brain.
Loads model on demand, unloads after use.
Only ONE model in RAM at a time = low RAM usage.
"""

import json
import time
from pathlib import Path

ROUTER_PATH = Path("data/model_router.json")

SYSTEM_PROMPT = """You are MMBA — Multi-Modular Brain Architecture.
You are a Senior Engineer AI assistant specialized in:
- PLC programming and ladder logic
- Industrial automation and SCADA
- Python programming
- Safety systems and protocols
- Engineering problem solving

Give ultra professional, precise, actionable responses.
Be direct. No unnecessary words."""

class ModelRouter:
    def __init__(self):
        self._router    = self._load_router()
        self._current   = None
        self._llm       = None

    def _load_router(self):
        try:
            with open(ROUTER_PATH) as f:
                return json.load(f)
        except:
            return {"models": {}, "routing": {}}

    def route(self, command: str) -> str:
        """Pick best model for this command."""
        cmd_l = command.lower()
        routing = self._router.get("routing", {})
        for keyword, model_key in routing.items():
            if keyword in cmd_l:
                return model_key
        return routing.get("default", "reasoning")

    def ask(self, command: str, context: str = "") -> str:
        """Ask the right model and get response."""
        model_key  = self.route(command)
        model_info = self._router.get("models", {}).get(model_key, {})

        if not model_info.get("ready"):
            return self._fallback(command)

        try:
            return self._ask_llm(model_info["file"], command, context)
        except Exception as e:
            return self._fallback(command)

    def _ask_llm(self, model_file: str, command: str, context: str) -> str:
        """Load model and get response — unload after."""
        try:
            from llama_cpp import Llama

            # Load model with strict RAM limits
            llm = Llama(
                model_path   = model_file,
                n_ctx        = 2048,    # context window
                n_threads    = 4,       # CPU threads
                n_gpu_layers = 0,       # CPU only — no GPU needed
                verbose      = False,
            )

            prompt = f"{SYSTEM_PROMPT}\n\nTask: {command}"
            if context:
                prompt += f"\nContext: {context}"

            start    = time.time()
            response = llm(
                prompt,
                max_tokens  = 512,
                temperature = 0.1,     # Low = more precise/professional
                stop        = ["Task:", "Human:", "\n\n\n"],
            )
            duration = time.time() - start

            # Unload model immediately — free RAM
            del llm

            text = response["choices"][0]["text"].strip()
            print(f"  [AI] Response in {duration:.1f}s")
            return text

        except ImportError:
            return self._fallback(command)
        except Exception as e:
            return self._fallback(command)

    def _fallback(self, command: str) -> str:
        """Fast rule-based fallback when no model available."""
        cmd = command.lower()
        if "ladder" in cmd or "plc" in cmd:
            return "PLC: Use NO contact → NC contact → Output coil. Check scan cycle and I/O mapping."
        if "python" in cmd or "code" in cmd:
            return "Python: Use modular design, separate concerns, handle exceptions properly."
        if "git" in cmd:
            return "Git: git add . && git commit -m 'message' && git push origin main"
        if "safety" in cmd:
            return "Safety: Verify E-stop, interlocks, watchdog timer, and SIL rating."
        return f"Processing: {command} — Please install AI models for full intelligence."

    def get_status(self) -> dict:
        models  = self._router.get("models", {})
        ready   = sum(1 for m in models.values() if m.get("ready"))
        return {
            "total_models": len(models),
            "ready_models": ready,
            "models": {k: v.get("ready") for k,v in models.items()},
        }
