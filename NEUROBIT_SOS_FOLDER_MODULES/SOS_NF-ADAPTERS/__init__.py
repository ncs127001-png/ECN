"""Adaptadores para integrar módulos externos en la Estación Central.

Cada adaptador expone send_message(envelope: dict, options: dict|None = None) -> dict
que normaliza el resultado y atrapa excepciones.
"""

from . import adapter_modulo_integrador  # noqa: F401
from . import adapter_llama_dispatcher_connector  # noqa: F401
from . import adapter_dispatcher_lite  # noqa: F401
from . import adapter_msg_sequencer  # noqa: F401
from . import adapter_msg_builder  # noqa: F401
from . import adapter_simon_validator  # noqa: F401
from . import adapter_sala_app  # noqa: F401

__all__ = [
    "adapter_modulo_integrador",
    "adapter_llama_dispatcher_connector",
    "adapter_dispatcher_lite",
    "adapter_msg_sequencer",
    "adapter_msg_builder",
    "adapter_simon_validator",
    "adapter_sala_app",
]
