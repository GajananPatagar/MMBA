#!/usr/bin/env python3
import sys, os, argparse
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.nervous_system import NervousSystem
from core.memory_manager import MemoryManager
from core.bus import VirtualBus
from modules.vision.vision_module import VisionModule
from modules.logic.logic_module import LogicModule
from modules.action.action_module import ActionModule
from modules.builder.builder_module import BuilderModule
from config.settings import Settings

BANNER = """
  MMBA — Multi-Modular Brain Architecture v1.0.0
  IHTM Department — Engineering Intelligence
"""

def main():
    print(BANNER)
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["auto","manual","train","status"], default="status")
    parser.add_argument("--ram-limit", type=int, default=900)
    parser.add_argument("--brain-path", default="./data/master_brain")
    args = parser.parse_args()

    settings = Settings(ram_limit_mb=args.ram_limit, brain_path=args.brain_path)
    bus      = VirtualBus()
    memory   = MemoryManager(limit_mb=args.ram_limit)
    ns       = NervousSystem(bus=bus, memory=memory, settings=settings)

    ns.register("vision",  VisionModule(bus, memory))
    ns.register("logic",   LogicModule(bus, memory, args.brain_path))
    ns.register("action",  ActionModule(bus, memory))
    ns.register("builder", BuilderModule(bus, memory))

    print(f"Mode: {args.mode.upper()}")
    if args.mode == "status":
        ns.print_status()
    elif args.mode == "manual":
        ns.interactive_shell()
    elif args.mode == "auto":
        ns.run_autonomous()
    elif args.mode == "train":
        ns.modules["builder"].run_training_loop()

if __name__ == "__main__":
    main()
