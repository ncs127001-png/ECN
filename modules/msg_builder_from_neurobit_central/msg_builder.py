#!/usr/bin/env python3
"""
msg_builder.py
Construye un mensaje YAML a partir de un archivo de texto o stdin.
Ejemplo:
  python3 msg_builder.py --source texto.txt --node TRON --session SALA1 --out message1.yaml
"""
import argparse, yaml, hashlib, uuid
from datetime import datetime

def sha1_short(text):
    import hashlib
    return hashlib.sha1(text.encode("utf-8")).hexdigest()[:12]

def build_message_doc(content, node, session, protocol, fragment_index, fragment_total):
    created = datetime.utcnow().isoformat() + "Z"
    message_id = str(uuid.uuid4())
    payload_for_hash = content + node + created
    message_hash = sha1_short(payload_for_hash)
    doc = {
        "PROTOCOL_ID": protocol,
        "VERSION": "0.1",
        "MESSAGE_ID": message_id,
        "SESSION_ID": session,
        "CREATED_AT": created,
        "ORIGEN": node,
        "MESSAGE_HASH": message_hash,
        "FRAGMENT": {
            "INDEX": fragment_index,
            "TOTAL": fragment_total,
            "TEMA": "general"
        },
        "TAGS": ["generated_by_msg_builder"],
        "CONTENT": content,
        "NOTES": ""
    }
    return doc, message_id


def main(envelope=None, argv=None):
    """Entry point. Can be called as main(envelope_dict) or main(argv=list).
    If the first arg is a dict it's treated as an envelope (programmatic call).
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", "-s", help="archivo de texto con el contenido", required=False)
    parser.add_argument("--node", "-n", help="NODE alias (ej: TRON)", required=False, default="UNKNOWN_NODE")
    parser.add_argument("--session", "-S", help="SESSION ID", default="SALA_01")
    parser.add_argument("--out", "-o", help="archivo yaml de salida", default=None)
    parser.add_argument("--protocol", help="PROTOCOL_ID", default="NEUROBIT_MSG_v0")
    parser.add_argument("--fragment-index", type=int, default=1)
    parser.add_argument("--fragment-total", type=int, default=1)
    # Support both calling conventions: main(envelope_dict) or main(argv=list)
    if isinstance(envelope, dict):
        args = parser.parse_args([])
        env = envelope
    else:
        # envelope not provided as first arg; maybe argv provided as first arg
        env = None
        parsed_argv = argv if argv is not None else envelope
        args = parser.parse_args(parsed_argv)

    if env is not None:
        content = str(env.get('content') or env.get('CONTENT') or env)
        node = env.get('entity_id') or env.get('ORIGEN') or env.get('origin') or args.node
        session = env.get('SESSION_ID') or env.get('session') or args.session
        protocol = env.get('PROTOCOL_ID') or args.protocol
        fragment_index = int(env.get('FRAGMENT', {}).get('INDEX', args.fragment_index) or args.fragment_index)
        fragment_total = int(env.get('FRAGMENT', {}).get('TOTAL', args.fragment_total) or args.fragment_total)
        out_file = args.out or f"message_{str(uuid.uuid4())[:8]}.yaml"
    else:
        if args.source:
            with open(args.source, "r", encoding="utf-8") as f:
                content = f.read().strip()
        else:
            import sys
            content = sys.stdin.read().strip()
        node = args.node
        session = args.session
        protocol = args.protocol
        fragment_index = args.fragment_index
        fragment_total = args.fragment_total
        out_file = args.out or f"message_{str(uuid.uuid4())[:8]}.yaml"

    if not content:
        print("No content provided.")
        raise SystemExit(1)

    doc, message_id = build_message_doc(content, node, session, protocol, fragment_index, fragment_total)

    with open(out_file, "w", encoding="utf-8") as f:
        yaml.safe_dump(doc, f, sort_keys=False, allow_unicode=True)

    print("Message generated:", out_file)


if __name__ == '__main__':
    main()
