"""A tiny mock dispatcher that simulates sending messages to external targets.

This mock simply returns a success dict and echoes back target info.
"""
import time

def send_message(envelope: dict) -> dict:
    """Simulate sending a message. Returns a result dict."""
    # Simulate network latency
    time.sleep(0.05)
    target = envelope.get('destination', envelope.get('entity_id', 'unknown'))
    return {
        'status': 'ok',
        'sent_to': target,
        'timestamp': time.strftime('%Y-%m-%dT%H:%M:%SZ'),
        'note': 'mock dispatched'
    }
