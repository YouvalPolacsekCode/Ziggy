import os
import json

MEMORY_FILE = os.path.join(os.path.dirname(__file__), "ziggy_memory.json")
_memory_store = {}

# ── Load memory from disk ──────────────────────────────────────
def load_memory():
    global _memory_store
    if os.path.exists(MEMORY_FILE):
        try:
            with open(MEMORY_FILE, "r", encoding="utf-8") as f:
                _memory_store = json.load(f)
            print("🧠 Memory loaded.")
        except Exception as e:
            print(f"[MEMORY LOAD ERROR] {e}")
            _memory_store = {}
    else:
        print("🧠 No existing memory file. Starting fresh.")
        _memory_store = {}

# ── Save memory to disk ────────────────────────────────────────
def save_memory():
    try:
        with open(MEMORY_FILE, "w", encoding="utf-8") as f:
            json.dump(_memory_store, f, ensure_ascii=False, indent=2)
        print("💾 Memory saved.")
    except Exception as e:
        print(f"[MEMORY SAVE ERROR] {e}")

# ── Save a topic to memory ─────────────────────────────────────
def save(topic, content):
    _memory_store[topic.lower()] = content
    save_memory()

# ── Retrieve a topic from memory ───────────────────────────────
def retrieve(topic):
    return _memory_store.get(topic.lower())
