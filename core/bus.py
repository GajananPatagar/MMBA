import queue, threading, time
from typing import Callable, Dict, List, Any

class Message:
    def __init__(self, sender, target, msg_type, payload):
        self.sender = sender
        self.target = target
        self.msg_type = msg_type
        self.payload = payload
        self.timestamp = time.time()

class VirtualBus:
    def __init__(self):
        self._queues = {}
        self._subscribers = {}
        self._lock = threading.Lock()
        self._message_log = []

    def register_module(self, name):
        with self._lock:
            self._queues[name] = queue.Queue()
        print(f"  [BUS] Module '{name}' registered.")

    def send(self, sender, target, msg_type, payload=None):
        msg = Message(sender, target, msg_type, payload)
        with self._lock:
            if target in self._queues:
                self._queues[target].put(msg)
                self._message_log.append(msg)
        return msg

    def publish(self, sender, event_type, payload=None):
        with self._lock:
            handlers = self._subscribers.get(event_type, [])
        for h in handlers:
            threading.Thread(target=h, args=(payload,), daemon=True).start()

    def subscribe(self, event_type, handler):
        with self._lock:
            if event_type not in self._subscribers:
                self._subscribers[event_type] = []
            self._subscribers[event_type].append(handler)

    def receive(self, module_name, timeout=1.0):
        try:
            return self._queues[module_name].get(timeout=timeout)
        except (queue.Empty, KeyError):
            return None

    def get_stats(self):
        return {
            "total_messages": len(self._message_log),
            "registered_modules": list(self._queues.keys()),
        }
