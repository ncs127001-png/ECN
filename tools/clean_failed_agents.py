#!/usr/bin/env python3
import json
from pathlib import Path

registry_file = Path("data/agents_registry.jsonl")
backup_file = Path("data/agents_registry.jsonl.backup")

# Backup
import shutil
shutil.copy2(registry_file, backup_file)

# Filtrar solo activos
active_agents = []
with open(registry_file, 'r') as f:
    for line in f:
        agent = json.loads(line)
        if agent.get('status') == 'active':
            active_agents.append(line)

# Reescribir
with open(registry_file, 'w') as f:
    f.writelines(active_agents)

print(f"✅ Limpiados {len(active_agents)} agentes activos")
print(f"📦 Backup en: {backup_file}")
