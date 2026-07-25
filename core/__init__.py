"""
NEUROBIT CORE PACKAGE - Estación Central Neurobitrónica v0.2
Soberanía Cognitiva y Técnica - localhost only
"""

# Exponer módulos críticos para imports directos desde 'core'
__all__ = [
    "participants",
    "coherence_filter", 
    "agents_registry",
    "init_ceremony",
    "centinela_monitor",
    "matrix_13x13",
    "members_registry",
    "sala_ronda_manager",
    "path_resolver"
]

# Imports explícitos para resolver el problema de rutas
from . import participants
from . import coherence_filter
from . import agents_registry
from . import init_ceremony
from . import centinela_monitor
from . import matrix_13x13
from . import members_registry
from . import sala_ronda_manager
from . import path_resolver

# Subpaquetes
from . import llm
from . import adapters
