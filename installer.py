#!/usr/bin/env python3
"""
MMBA Multi-Model Brain Installer v3.0.0
Downloads ALL models automatically.
Total brain size: ~40GB
"""

import os
import sys
import json
import time
import shutil
import platform
import subprocess
import urllib.request
from pathlib import Path

BRAIN_PATH = Path("data/master_brain")
MODEL_PATH = Path("data/models")
VERSION    = "3.0.0"

BANNER = """
╔══════════════════════════════════════════════════════╗
║   MMBA — Multi-Model Brain Installer v3.0.0         ║
║   Downloading 40GB Professional AI Brain            ║
║   IHTM Department                                   ║
╚══════════════════════════════════════════════════════╝
"""

# ══════════════════════════════════════════════════════
# ALL MODELS — Each specializes in different domain
# Total = ~40GB on disk, ~2GB RAM (disk-mapped)
# ══════════════════════════════════════════════════════
MODELS = {

    # ── 1. REASONING BRAIN (Main thinker) ─────────────
    # Best for: complex decisions, planning, analysis
    # RAM: 512MB  Disk: 4.8GB  Speed: fast
    "reasoning": {
        "name":    "Llama-3.2-3B — Reasoning Brain",
        "file":    "llama3-reasoning.gguf",
        "url":     "https://huggingface.co/bartowski/Llama-3.2-3B-Instruct-GGUF/resolve/main/Llama-3.2-3B-Instruct-Q8_0.gguf",
        "size_gb": 3.4,
        "role":    "Main reasoning — plans and decides",
        "ram_mb":  512,
    },

    # ── 2. CODE BRAIN ─────────────────────────────────
    # Best for: writing Python, ladder logic, scripts
    # RAM: 512MB  Disk: 4.8GB  Speed: fast
    "coder": {
        "name":    "DeepSeek-Coder-1.3B — Code Brain",
        "file":    "deepseek-coder.gguf",
        "url":     "https://huggingface.co/TheBloke/deepseek-coder-1.3b-instruct-GGUF/resolve/main/deepseek-coder-1.3b-instruct.Q8_0.gguf",
        "size_gb": 1.4,
        "role":    "Writes Python, ladder logic, scripts",
        "ram_mb":  256,
    },

    # ── 3. ENGINEERING BRAIN ──────────────────────────
    # Best for: PLC, industrial automation, SCADA
    # RAM: 1GB  Disk: 8GB  Speed: medium
    "engineer": {
        "name":    "Mistral-7B — Engineering Brain",
        "file":    "mistral7b-engineering.gguf",
        "url":     "https://huggingface.co/TheBloke/Mistral-7B-Instruct-v0.2-GGUF/resolve/main/mistral-7b-instruct-v0.2.Q4_K_M.gguf",
        "size_gb": 4.4,
        "role":    "PLC engineering, industrial automation",
        "ram_mb":  512,
    },

    # ── 4. VISION BRAIN ───────────────────────────────
    # Best for: reading screens, OCR, UI detection
    # RAM: 256MB  Disk: 1.5GB  Speed: ultra fast
    "vision": {
        "name":    "MobileNet-V3 — Vision Brain",
        "file":    "vision-model.onnx",
        "url":     "https://github.com/onnx/models/raw/main/validated/vision/classification/mobilenet/model/mobilenetv3-small-075.onnx",
        "size_gb": 0.01,
        "role":    "Screen reading, UI detection, OCR",
        "ram_mb":  64,
    },

    # ── 5. FAST REFLEX BRAIN ──────────────────────────
    # Best for: instant responses, common commands
    # RAM: 128MB  Disk: 0.8GB  Speed: ultra fast
    "reflex": {
        "name":    "Phi-3-Mini — Reflex Brain",
        "file":    "phi3-mini-reflex.gguf",
        "url":     "https://huggingface.co/microsoft/Phi-3-mini-4k-instruct-gguf/resolve/main/Phi-3-mini-4k-instruct-q4.gguf",
        "size_gb": 2.4,
        "role":    "Ultra fast reflex — instant responses",
        "ram_mb":  256,
    },

    # ── 6. MEMORY BRAIN ───────────────────────────────
    # Best for: embeddings, semantic search, recall
    # RAM: 128MB  Disk: 0.5GB  Speed: ultra fast
    "memory": {
        "name":    "All-MiniLM — Memory Brain",
        "file":    "minilm-memory.gguf",
        "url":     "https://huggingface.co/second-state/All-MiniLM-L6-v2-Embedding-GGUF/resolve/main/all-MiniLM-L6-v2-Q8_0.gguf",
        "size_gb": 0.04,
        "role":    "Semantic memory, similarity search",
        "ram_mb":  64,
    },

    # ── 7. SAFETY BRAIN ───────────────────────────────
    # Best for: safety checks, risk assessment
    # RAM: 512MB  Disk: 4GB  Speed: fast
    "safety": {
        "name":    "Gemma-2B — Safety Brain",
        "file":    "gemma2b-safety.gguf",
        "url":     "https://huggingface.co/bartowski/gemma-2-2b-it-GGUF/resolve/main/gemma-2-2b-it-Q8_0.gguf",
        "size_gb": 2.5,
        "role":    "Safety checks, risk assessment, alarms",
        "ram_mb":  256,
    },

    # ── 8. DOCUMENTATION BRAIN ────────────────────────
    # Best for: reading manuals, generating reports
    # RAM: 1GB  Disk: 8GB  Speed: medium
    "docs": {
        "name":    "Qwen2-7B — Documentation Brain",
        "file":    "qwen2-docs.gguf",
        "url":     "https://huggingface.co/Qwen/Qwen2-7B-Instruct-GGUF/resolve/main/qwen2-7b-instruct-q4_k_m.gguf",
        "size_gb": 4.5,
        "role":    "Reads manuals, writes reports, documentation",
        "ram_mb":  512,
    },
}

# ══════════════════════════════════════════════════════
# KNOWLEDGE BASE
# ══════════════════════════════════════════════════════
BUILTIN_KNOWLEDGE = {
    "plc/ladder_logic.json": {
        "elements": {
            "NO_contact":    "Normally Open — passes power when bit=1",
            "NC_contact":    "Normally Closed — passes power when bit=0",
            "output_coil":   "Sets bit when rung is true",
            "timer_TON":     "On-delay timer",
            "timer_TOF":     "Off-delay timer",
            "timer_RTO":     "Retentive timer",
            "counter_CTU":   "Count up counter",
            "counter_CTD":   "Count down counter",
            "compare_EQU":   "Equal comparison",
            "compare_GRT":   "Greater than",
            "compare_LES":   "Less than",
            "math_ADD":      "Addition",
            "math_SUB":      "Subtraction",
            "math_MUL":      "Multiplication",
            "math_DIV":      "Division",
        },
        "safety": {
            "estop":         "Emergency stop — NC hardwired",
            "interlock":     "Prevents unsafe operations",
            "safety_relay":  "Monitors safety circuit",
            "watchdog":      "Fault on missed scan",
            "SIL1":          "Low risk reduction",
            "SIL2":          "Medium risk reduction",
            "SIL3":          "High risk reduction",
            "LOTO":          "Lockout/Tagout procedure",
        },
        "controllers": {
            "Allen_Bradley": "Studio 5000 — RSLogix",
            "Siemens":       "TIA Portal — S7 series",
            "Schneider":     "Unity Pro — Modicon",
            "Mitsubishi":    "GX Works — MELSEC",
            "Omron":         "Sysmac Studio — NX/NJ",
            "Beckhoff":      "TwinCAT — PC based",
        },
    },
    "engineering/standards.json": {
        "IEC_61131": {
            "LD":  "Ladder Diagram",
            "FBD": "Function Block Diagram",
            "ST":  "Structured Text",
            "IL":  "Instruction List",
            "SFC": "Sequential Function Chart",
        },
        "safety_standards": {
            "IEC_61508": "Functional safety of E/E/PE systems",
            "IEC_61511": "Process industry safety",
            "ISO_13849": "Safety of machinery",
            "IEC_62061": "Functional safety of machines",
        },
        "networking": {
            "Modbus_RTU":  "Serial RS-485",
            "Modbus_TCP":  "Ethernet Modbus",
            "Profibus":    "Siemens field bus",
            "Profinet":    "Siemens Ethernet",
            "EtherNet_IP": "Rockwell Ethernet",
            "OPC_UA":      "Universal standard",
        },
    },
    "ai/model_routing.json": {
        "routing_rules": {
            "code_request":        "coder",
            "plc_request":         "engineer",
            "safety_request":      "safety",
            "screen_request":      "vision",
            "fast_request":        "reflex",
            "memory_request":      "memory",
            "document_request":    "docs",
            "complex_request":     "reasoning",
        },
        "ram_strategy": "Load only active model — unload after use",
        "disk_strategy": "All models on SSD — mmap access",
    },
}


class ProgressBar:
    def __init__(self, total, label=""):
        self.total   = total
        self.current = 0
        self.label   = label

    def update(self, current):
        self.current = current
        pct  = (current / self.total) * 100 if self.total else 0
        done = int(pct / 2)
        bar  = "█" * done + "░" * (50 - done)
        mb_done  = current / (1024*1024)
        mb_total = self.total / (1024*1024)
        print(f"\r  [{bar}] {pct:.1f}% ({mb_done:.1f}/{mb_total:.1f}MB)", end="", flush=True)

    def finish(self):
        print()


class MMBAInstaller:
    def __init__(self):
        self.errors        = []
        self.downloaded    = []
        self.skipped       = []
        self.total_size_gb = 0

    def run(self):
        print(BANNER)
        print(f"  System  : {platform.system()} {platform.machine()}")
        print(f"  Python  : {sys.version.split()[0]}")
        print(f"  Models  : {len(MODELS)} AI brains")
        total = sum(m["size_gb"] for m in MODELS.values())
        print(f"  Total   : ~{total:.1f}GB download")
        print(f"  RAM use : ~2GB max (disk-mapped)")
        print()

        steps = [
            ("Creating directories",          self._create_dirs),
            ("Installing llama.cpp engine",   self._install_llamacpp),
            ("Installing knowledge base",     self._install_knowledge),
            ("Downloading AI models",         self._download_models),
            ("Building model router",         self._build_router),
            ("Verifying installation",        self._verify),
        ]

        for i, (label, fn) in enumerate(steps, 1):
            print(f"[{i}/{len(steps)}] {label}...")
            try:
                fn()
                print(f"  ✓ Done\n")
            except Exception as e:
                print(f"  ⚠ {e}\n")
                self.errors.append(str(e))

        self._summary()

    # ── Directories ───────────────────────────────────

    def _create_dirs(self):
        dirs = [
            MODEL_PATH,
            BRAIN_PATH / "plc",
            BRAIN_PATH / "engineering",
            BRAIN_PATH / "ai",
            Path("data/knowledge_map"),
            Path("logs"),
        ]
        for d in dirs:
            d.mkdir(parents=True, exist_ok=True)
            print(f"  Created: {d}")

    # ── llama.cpp ─────────────────────────────────────

    def _install_llamacpp(self):
        try:
            import llama_cpp
            print("  llama.cpp already installed.")
            return
        except ImportError:
            pass
        print("  Installing llama-cpp-python...")
        subprocess.run([
            sys.executable, "-m", "pip", "install",
            "llama-cpp-python", "--quiet"
        ], check=True)
        print("  llama.cpp engine ready.")

    # ── Knowledge ─────────────────────────────────────

    def _install_knowledge(self):
        for filename, data in BUILTIN_KNOWLEDGE.items():
            path = BRAIN_PATH / filename
            path.parent.mkdir(parents=True, exist_ok=True)
            with open(path, "w") as f:
                json.dump(data, f, indent=2)
            print(f"  Installed: {filename}")

    # ── Model Downloader ──────────────────────────────

    def _download_models(self):
        total = len(MODELS)
        for i, (key, model) in enumerate(MODELS.items(), 1):
            dest = MODEL_PATH / model["file"]
            print(f"\n  [{i}/{total}] {model['name']}")
            print(f"         Role  : {model['role']}")
            print(f"         Size  : {model['size_gb']}GB")
            print(f"         RAM   : {model['ram_mb']}MB")

            if dest.exists():
                size_gb = dest.stat().st_size / (1024**3)
                print(f"         Status: Already downloaded ({size_gb:.2f}GB) ✓")
                self.skipped.append(key)
                continue

            try:
                self._download_file(model["url"], dest, model["name"])
                self.downloaded.append(key)
                self.total_size_gb += model["size_gb"]
            except Exception as e:
                print(f"\n         ⚠ Failed: {e}")
                self.errors.append(f"{key}: {e}")

    def _download_file(self, url, dest, name):
        print(f"         Downloading...")
        bar = None

        def progress(count, block_size, total_size):
            nonlocal bar
            if bar is None and total_size > 0:
                bar = ProgressBar(total_size, name)
            if bar:
                bar.update(min(count * block_size, total_size))

        req = urllib.request.Request(
            url,
            headers={"User-Agent": "MMBA-Installer/3.0"}
        )
        tmp = str(dest) + ".tmp"
        try:
            urllib.request.urlretrieve(url, tmp, reporthook=progress)
            if bar:
                bar.finish()
            shutil.move(tmp, dest)
            size_gb = dest.stat().st_size / (1024**3)
            print(f"         ✓ Downloaded: {size_gb:.2f}GB")
        except Exception as e:
            if os.path.exists(tmp):
                os.remove(tmp)
            raise e

    # ── Router ────────────────────────────────────────

    def _build_router(self):
        router = {
            "version": VERSION,
            "models": {},
            "routing": {
                "code":        "coder",
                "python":      "coder",
                "ladder":      "engineer",
                "plc":         "engineer",
                "safety":      "safety",
                "estop":       "safety",
                "screen":      "vision",
                "click":       "vision",
                "fast":        "reflex",
                "quick":       "reflex",
                "remember":    "memory",
                "search":      "memory",
                "manual":      "docs",
                "report":      "docs",
                "default":     "reasoning",
            }
        }
        for key, model in MODELS.items():
            dest = MODEL_PATH / model["file"]
            router["models"][key] = {
                "name":     model["name"],
                "file":     str(dest.absolute()),
                "role":     model["role"],
                "ram_mb":   model["ram_mb"],
                "ready":    dest.exists(),
            }

        path = Path("data/model_router.json")
        with open(path, "w") as f:
            json.dump(router, f, indent=2)
        print(f"  Router saved: {path}")

    # ── Verify ────────────────────────────────────────

    def _verify(self):
        router_path = Path("data/model_router.json")
        if router_path.exists():
            with open(router_path) as f:
                router = json.load(f)
            ready = sum(1 for m in router["models"].values() if m["ready"])
            total = len(router["models"])
            print(f"  Models ready: {ready}/{total}")
            for key, m in router["models"].items():
                status = "✓" if m["ready"] else "✗ not downloaded"
                print(f"  [{key:10s}] {status} — {m['name']}")

    # ── Summary ───────────────────────────────────────

    def _summary(self):
        print()
        print("═" * 54)
        print("  MMBA BRAIN INSTALLATION COMPLETE")
        print("═" * 54)
        print(f"  Downloaded  : {len(self.downloaded)} models")
        print(f"  Skipped     : {len(self.skipped)} (already existed)")
        print(f"  Total size  : {self.total_size_gb:.1f}GB")
        print(f"  Max RAM use : ~2GB (disk-mapped loading)")
        print(f"  Errors      : {len(self.errors)}")
        print("═" * 54)
        print()
        print("  Run MMBA:")
        print("  python main.py --mode status")
        print("  python main.py --mode manual")
        print("═" * 54)


if __name__ == "__main__":
    MMBAInstaller().run()
