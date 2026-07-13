# tools/session_hash.py
#!/usr/bin/env python3
import hashlib, json, datetime

def hash_session(message: str):
    entry = {
        "timestamp": datetime.datetime.now().isoformat(),
        "content_hash": hashlib.sha256(message.encode()).hexdigest(),
        "message": message[:100] + "..."  # Preview
    }
    with open("/tmp/session_evidence.jsonl", "a") as f:
        f.write(json.dumps(entry) + "\n")
    print(f"✅ Evidencia registrada: {entry['content_hash'][:12]}")