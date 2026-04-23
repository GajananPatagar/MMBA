import os, gc, time, json, threading
try:
    import psutil
    HAS_PSUTIL = True
except ImportError:
    HAS_PSUTIL = False

class MemoryManager:
    def __init__(self, limit_mb=900):
        self.limit_mb = limit_mb
        self._cache = {}
        self._access = {}
        self._lock = threading.Lock()
        print(f"  [MEM] Memory Manager active. Budget: {limit_mb}MB")

    def current_usage_mb(self):
        if HAS_PSUTIL:
            try:
                return psutil.Process(os.getpid()).memory_info().rss / (1024*1024)
            except:
                pass
        return 0.0

    def is_safe(self):
        return self.current_usage_mb() < (self.limit_mb * 0.90)

    def usage_report(self):
        used = self.current_usage_mb()
        return {
            "used_mb": round(used, 2),
            "limit_mb": self.limit_mb,
            "available_mb": round(max(0, self.limit_mb - used), 2),
            "usage_pct": round((used / self.limit_mb) * 100, 1),
            "status": "OK" if self.is_safe() else "WARNING",
            "cached_items": len(self._cache),
        }

    def store(self, key, value, estimated_bytes=0):
        if not self.is_safe():
            self._evict()
        with self._lock:
            self._cache[key] = value
            self._access[key] = time.time()

    def retrieve(self, key):
        with self._lock:
            if key in self._cache:
                self._access[key] = time.time()
                return self._cache[key]
        return None

    def _evict(self):
        with self._lock:
            if not self._access:
                return
            lru = min(self._access, key=self._access.get)
            self._cache.pop(lru, None)
            self._access.pop(lru, None)
        gc.collect()

    def load_knowledge_index(self, path):
        try:
            with open(path) as f:
                return json.load(f)
        except:
            return {}
