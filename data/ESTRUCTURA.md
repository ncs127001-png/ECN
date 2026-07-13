WORKSPACE_NEUROBIT_V0.3/
├── data/                       # ANILLO 4 (Persistencia e Inmunidad Local)
│   ├── declaraciones_base.yaml # La receta mnemotécnica global (El Mapa del Todo)
│   ├── memoria_eva.jsonl       # El Arca append-only (3.1 MB, inmutable)
│   └── tareas_pendientes.jsonl # Cola de despacho de interrupciones del Centinela
│
├── core/                       # ANILLO 1 y 2 (Kernel de Coherencia e Interrupciones)
│   ├── __init__.py
│   ├── neurobit_core_v03.py    # Motor In-Memory (Carga de los 20,477 Hexagramas en RAM)
│   ├── neurobit_declarator.py  # El Artefacto Lector de Declaraciones Ajustado
│   ├── coherence_filter.py     # Filtro M/E de Análisis Ortolingüístico
│   ├── matrix_13x13.py         # Backend fractal de la Matriz Radial de 169 celdas
│   ├── centinela_monitor.py    # Daemon de escucha pasiva del clipboard
│   └── hid_events.py           # Traductor de scancodes nativos de /dev/input/event*
│
├── mcp_server/                 # ANILLO 3 (Punteros e Interfaces de Control)
│   ├── __init__.py
│   └── neurobit_mcp_server.py  # El Bastión Autónomo Local en el puerto :8090
│
├── daemons/                    # ANILLO 5 (Perímetro Exterior / El Anillo Negro)
│   ├── neurobit_hid_daemon.py  # Driver USB Virtual a nivel de Kernel (Mímesis HID)
│   └── ide_audit_daemon.py     # Auto-kill quirúrgico de procesos huérfanos del sistema
│
└── compile_project.py          # Herramienta de filtrado y empaquetado agresivo

