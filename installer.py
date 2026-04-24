#!/usr/bin/env python3
"""
MMBA Auto-Installer
Downloads and builds the complete brain automatically.
"""

import os
import sys
import json
import time
import shutil
import zipfile
import urllib.request
import subprocess
import platform
from pathlib import Path

BRAIN_PATH = Path("data/master_brain")
VERSION = "1.0.0"

BANNER = """
╔══════════════════════════════════════════════════╗
║   MMBA — Multi-Modular Brain Architecture        ║
║   Auto-Installer v1.0.0                         ║
║   IHTM Department                               ║
╚══════════════════════════════════════════════════╝
"""

# ── Knowledge sources (free, open datasets) ────────────────────
KNOWLEDGE_SOURCES = {
    "python_docs": {
        "url": "https://docs.python.org/3/library/",
        "type": "scrape",
        "topics": ["functions","classes","modules","exceptions"],
    },
    "wikipedia_engineering": {
        "url": "https://en.wikipedia.org/wiki/",
        "type": "wiki",
        "topics": [
            "Programmable_logic_controller",
            "Ladder_logic",
            "Industrial_automation",
            "SCADA",
            "PID_controller",
            "Safety_instrumented_system",
            "Distributed_control_system",
            "Human_machine_interface",
            "Modbus",
            "Profibus",
            "EtherNet/IP",
            "IEC_61131-3",
        ],
    },
}

# ── Built-in knowledge (always installed, no download needed) ──
BUILTIN_KNOWLEDGE = {
    "plc/ladder_logic.json": {
        "elements": {
            "NO_contact": "Normally Open — passes power when bit=1",
            "NC_contact": "Normally Closed — passes power when bit=0",
            "output_coil": "Sets bit when rung is true",
            "timer_TON": "On-delay timer — activates after preset time",
            "timer_TOF": "Off-delay timer — deactivates after preset time",
            "timer_RTO": "Retentive timer — holds value on power loss",
            "counter_CTU": "Count up counter",
            "counter_CTD": "Count down counter",
            "counter_CTUD": "Count up/down counter",
            "move_MOV": "Move data from source to destination",
            "compare_EQU": "Equal — true when A equals B",
            "compare_NEQ": "Not Equal — true when A not equals B",
            "compare_GRT": "Greater Than — true when A > B",
            "compare_LES": "Less Than — true when A < B",
            "compare_GEQ": "Greater or Equal — true when A >= B",
            "compare_LEQ": "Less or Equal — true when A <= B",
            "math_ADD": "Addition — adds two values",
            "math_SUB": "Subtraction — subtracts two values",
            "math_MUL": "Multiplication — multiplies two values",
            "math_DIV": "Division — divides two values",
            "math_MOD": "Modulo — remainder of division",
            "math_SQR": "Square root",
            "math_ABS": "Absolute value",
            "jump_JMP": "Jump to label in program",
            "jump_LBL": "Label — destination for JMP",
            "jump_JSR": "Jump to subroutine",
            "jump_RET": "Return from subroutine",
            "file_COP": "Copy file of data",
            "file_FLL": "Fill file with value",
            "bit_AND": "Bitwise AND",
            "bit_OR":  "Bitwise OR",
            "bit_XOR": "Bitwise XOR",
            "bit_NOT": "Bitwise NOT",
        },
        "safety": {
            "estop": "Emergency stop — NC contact hardwired in series",
            "interlock": "Prevents unsafe simultaneous operations",
            "safety_relay": "Monitors safety circuit integrity",
            "fault_routine": "Program executed on controller fault",
            "watchdog": "Timer that resets on healthy scan, faults on miss",
            "redundancy": "Dual controllers for critical systems",
            "SIL1": "Safety Integrity Level 1 — low risk reduction",
            "SIL2": "Safety Integrity Level 2 — medium risk reduction",
            "SIL3": "Safety Integrity Level 3 — high risk reduction",
            "LOTO": "Lockout/Tagout — energy isolation procedure",
        },
        "scan_cycle": {
            "input_scan": "Read all input states into memory table",
            "program_scan": "Execute ladder logic top to bottom left to right",
            "output_scan": "Write memory states to physical outputs",
            "housekeeping": "Controller diagnostics communications overhead",
            "scan_time": "Typical 1-20ms depending on program size",
        },
        "controllers": {
            "Allen_Bradley": "Rockwell Automation — Studio 5000 software",
            "Siemens": "S7-300 S7-400 S7-1200 S7-1500 — TIA Portal",
            "Schneider": "Modicon M340 M580 — Unity Pro",
            "Mitsubishi": "MELSEC series — GX Works",
            "Omron": "CJ2 NJ NX series — Sysmac Studio",
            "Beckhoff": "TwinCAT — PC-based control",
        },
        "networking": {
            "Modbus_RTU": "Serial RS-485 master-slave protocol",
            "Modbus_TCP": "Ethernet version of Modbus",
            "Profibus": "Siemens process field bus",
            "Profinet": "Siemens industrial Ethernet",
            "EtherNet_IP": "Rockwell industrial Ethernet",
            "DeviceNet": "Low-level device network",
            "CANopen": "CAN bus application layer",
            "OPC_UA": "Unified architecture — platform independent",
        },
    },
    "python/patterns.json": {
        "design_patterns": {
            "singleton": "One instance only — use for shared resources",
            "factory": "Create objects without specifying exact class",
            "observer": "Notify multiple objects of state changes",
            "strategy": "Swap algorithms at runtime",
            "module": "Separate concerns into independent files",
            "decorator": "Add behavior to objects dynamically",
            "facade": "Simplified interface to complex subsystem",
            "adapter": "Convert interface to another interface",
            "command": "Encapsulate request as object",
            "state": "Object behavior changes with internal state",
        },
        "memory_tips": {
            "generators": "Use yield instead of return for large data",
            "mmap": "Memory-map large files instead of loading all",
            "slots": "Use __slots__ to reduce object memory by 40%",
            "gc": "Call gc.collect() after deleting large objects",
            "chunks": "Read large files in 4096 byte chunks",
            "weakref": "Use weakref for cache that can be garbage collected",
            "array": "Use array module instead of list for numbers",
            "numpy": "Use numpy arrays for numerical computation",
        },
        "best_practices": {
            "naming": "snake_case variables PascalCase classes UPPER_CASE constants",
            "errors": "Always use try/except with specific exceptions",
            "logging": "Use logging module not print for production",
            "testing": "Write tests before or alongside code — TDD",
            "comments": "Explain WHY not WHAT in comments",
            "type_hints": "Use type hints for better code clarity",
            "docstrings": "Document every public function and class",
            "pep8": "Follow PEP8 style guide always",
        },
        "threading": {
            "daemon": "Daemon threads die when main thread exits",
            "lock": "threading.Lock() prevents race conditions",
            "queue": "queue.Queue() is thread-safe communication",
            "event": "threading.Event() for signaling between threads",
            "semaphore": "Limit concurrent access to resource",
        },
    },
    "engineering/standards.json": {
        "IEC_61131": {
            "part1": "General information",
            "part2": "Equipment requirements and tests",
            "part3": "Programming languages — LD IL FBD ST SFC",
            "part4": "User guidelines",
            "part5": "Communications — function blocks",
            "part6": "Functional safety",
            "part7": "Fuzzy control",
            "part8": "Guidelines for application and implementation",
            "LD": "Ladder Diagram — graphical relay equivalent",
            "IL": "Instruction List — assembly-like text",
            "FBD": "Function Block Diagram — graphical data flow",
            "ST": "Structured Text — Pascal-like high level",
            "SFC": "Sequential Function Chart — Grafcet-based",
        },
        "ISA_standards": {
            "ISA5.1": "Instrumentation symbols and identification",
            "ISA18.2": "Management of alarm systems",
            "ISA88": "Batch control",
            "ISA95": "Enterprise-control system integration",
            "ISA99": "Industrial cybersecurity",
            "ISA100": "Wireless systems for automation",
        },
        "safety_standards": {
            "IEC_61508": "Functional safety of E/E/PE systems",
            "IEC_62061": "Safety of machinery — functional safety",
            "ISO_13849": "Safety of machinery — safety-related parts",
            "IEC_61511": "Functional safety — process industry",
            "NFPA_70E": "Electrical safety in the workplace",
            "OSHA_1910": "General industry safety standards",
        },
        "instrumentation": {
            "4_20mA": "Standard analog signal — 4mA=0% 20mA=100%",
            "0_10V": "Voltage analog signal",
            "RTD": "Resistance Temperature Detector — PT100 PT1000",
            "thermocouple": "Type J K T E — temperature measurement",
            "pressure_transmitter": "Measures process pressure",
            "flow_meter": "Measures process flow rate",
            "level_sensor": "Measures tank or vessel level",
            "pH_sensor": "Measures acidity alkalinity",
            "vibration": "Monitors rotating equipment health",
        },
    },
    "engineering/troubleshooting.json": {
        "plc_faults": {
            "I/O_fault": "Check wiring, fuse, power supply to field device",
            "comm_fault": "Check cables, termination resistors, baud rate",
            "memory_fault": "Clear memory, reload program, check battery",
            "watchdog_fault": "Program scan too long — optimize code",
            "power_fault": "Check input voltage, UPS, power supply output",
            "battery_low": "Replace battery — program memory at risk",
        },
        "ladder_debug": {
            "rung_false": "Trace from left — find first open element",
            "output_on": "Check for conflicting outputs same address",
            "timer_not_timing": "Check enable rung is true continuously",
            "counter_not_counting": "Check for one-shot on input rung",
            "forced_IO": "Check for forced I/O — may override logic",
        },
        "common_issues": {
            "noise": "Add RC snubbers, shield cables, separate power",
            "ground_loop": "Use isolated inputs or signal conditioners",
            "voltage_drop": "Check wire gauge, connection resistance",
            "EMI": "Route signal cables away from power cables",
        },
    },
    "ai/machine_learning.json": {
        "concepts": {
            "supervised": "Learn from labeled examples",
            "unsupervised": "Find patterns in unlabeled data",
            "reinforcement": "Learn from rewards and penalties",
            "neural_network": "Layers of connected nodes mimicking brain",
            "transformer": "Attention-based architecture for sequences",
            "fine_tuning": "Adapt pretrained model to specific task",
            "inference": "Running model to get predictions",
            "training": "Adjusting model weights from data",
        },
        "optimization": {
            "quantization": "Reduce model precision — less RAM",
            "pruning": "Remove unimportant weights — smaller model",
            "distillation": "Train small model to mimic large model",
            "mmap_loading": "Load model weights on demand from disk",
            "batch_size": "Smaller batch = less RAM more time",
            "gradient_checkpointing": "Trade compute for memory",
        },
    },
}


class BrainInstaller:
    def __init__(self):
        self.total_files = 0
        self.total_size  = 0
        self.errors      = []

    def run(self):
        print(BANNER)
        print(f"  System  : {platform.system()} {platform.machine()}")
        print(f"  Python  : {sys.version.split()[0]}")
        print(f"  Brain   : {BRAIN_PATH.absolute()}")
        print()

        steps = [
            ("Creating brain directories",    self._create_dirs),
            ("Installing built-in knowledge", self._install_builtin),
            ("Downloading Wikipedia data",    self._download_wiki),
            ("Building knowledge index",      self._build_index),
            ("Verifying installation",        self._verify),
        ]

        for i, (label, fn) in enumerate(steps, 1):
            print(f"[{i}/{len(steps)}] {label}...")
            try:
                fn()
                print(f"  ✓ Done\n")
            except Exception as e:
                print(f"  ⚠ Warning: {e}\n")
                self.errors.append(str(e))

        self._print_summary()

    def _create_dirs(self):
        dirs = [
            BRAIN_PATH,
            BRAIN_PATH / "plc",
            BRAIN_PATH / "python",
            BRAIN_PATH / "engineering",
            BRAIN_PATH / "ai",
            BRAIN_PATH / "wiki",
            Path("data/knowledge_map"),
            Path("logs"),
        ]
        for d in dirs:
            d.mkdir(parents=True, exist_ok=True)
            print(f"  Created: {d}")

    def _install_builtin(self):
        for filename, data in BUILTIN_KNOWLEDGE.items():
            path = BRAIN_PATH / filename
            path.parent.mkdir(parents=True, exist_ok=True)
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
            size = path.stat().st_size
            self.total_size += size
            self.total_files += 1
            print(f"  Installed: {filename} ({size/1024:.1f}KB)")

    def _download_wiki(self):
        topics = KNOWLEDGE_SOURCES["wikipedia_engineering"]["topics"]
        wiki_dir = BRAIN_PATH / "wiki"
        print(f"  Downloading {len(topics)} Wikipedia articles...")

        for topic in topics:
            try:
                url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{topic}"
                req = urllib.request.Request(
                    url,
                    headers={"User-Agent": "MMBA-Installer/1.0"}
                )
                with urllib.request.urlopen(req, timeout=10) as r:
                    data = json.loads(r.read().decode())

                article = {
                    "title":   data.get("title", topic),
                    "summary": data.get("extract", ""),
                    "url":     data.get("content_urls", {}).get("desktop", {}).get("page", ""),
                }

                fname = wiki_dir / f"{topic.replace('/', '_')}.json"
                with open(fname, "w", encoding="utf-8") as f:
                    json.dump(article, f, indent=2, ensure_ascii=False)

                size = fname.stat().st_size
                self.total_size += size
                self.total_files += 1
                print(f"  ✓ {data.get('title', topic)} ({size/1024:.1f}KB)")
                time.sleep(0.3)  # Be polite to Wikipedia

            except Exception as e:
                print(f"  ⚠ Skipped {topic}: {e}")

    def _build_index(self):
        index = {
            "version":      VERSION,
            "installed_at": time.strftime("%Y-%m-%d %H:%M:%S"),
            "platform":     platform.system(),
            "domains":      {},
            "total_files":  0,
            "total_size_kb": 0,
        }

        for domain_dir in BRAIN_PATH.iterdir():
            if domain_dir.is_dir():
                files = list(domain_dir.glob("*.json"))
                domain_size = sum(f.stat().st_size for f in files)
                index["domains"][domain_dir.name] = {
                    "files":   [f.name for f in files],
                    "count":   len(files),
                    "size_kb": round(domain_size / 1024, 1),
                }

        index["total_files"]   = self.total_files
        index["total_size_kb"] = round(self.total_size / 1024, 1)

        with open(BRAIN_PATH / "index.json", "w") as f:
            json.dump(index, f, indent=2)

        print(f"  Index built: {self.total_files} files")

    def _verify(self):
        required = [
            BRAIN_PATH / "index.json",
            BRAIN_PATH / "plc" / "ladder_logic.json",
            BRAIN_PATH / "python" / "patterns.json",
            BRAIN_PATH / "engineering" / "standards.json",
        ]
        for path in required:
            if path.exists():
                print(f"  ✓ {path}")
            else:
                print(f"  ✗ MISSING: {path}")
                self.errors.append(f"Missing: {path}")

    def _print_summary(self):
        print("=" * 52)
        print("  MMBA BRAIN INSTALLATION COMPLETE")
        print("=" * 52)
        print(f"  Files installed : {self.total_files}")
        print(f"  Total size      : {self.total_size/1024:.1f} KB")
        print(f"  Brain location  : {BRAIN_PATH.absolute()}")
        print(f"  Errors          : {len(self.errors)}")
        print("=" * 52)
        if self.errors:
            print("  Warnings (non-fatal):")
            for e in self.errors:
                print(f"    - {e}")
        print()
        print("  Run MMBA with:")
        print("  python main.py --mode status")
        print("  python main.py --mode manual")
        print("=" * 52)


if __name__ == "__main__":
    installer = BrainInstaller()
    installer.run()
