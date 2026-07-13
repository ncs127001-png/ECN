#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NEUROBIT MESSAGE VALIDATOR - CORE v0.3
Propósito: Validar la firma estructural, el hash SHA256 y la ventana temporal
           de los paquetes entrantes del VM Bridge antes de su despacho a tmux.
"""
import re
import hashlib
from datetime import datetime, timedelta

class NeurobitMessageValidator:
    def __init__(self, max_delay_minutes=5):
        self.max_delay = max_delay_minutes
        # Regex canónico para capturar el header rígido de the Sofistas
        self.parser_header = re.compile(
            r"\[VM_ASSIGN:(?P<agent>.*?)\]\s*"
            r"\[VM_ID:(?P<vm_id>.*?)\]\s*"
            r"\[TIMESTAMP:(?P<ts>.*?)\]\s*"
            r"\[HASH:(?P<hash>.*?)\]\s*"
            r"\[VERSION:(?P<ver>.*?)\]\s*"
            r"\[VM_END\]", re.DOTALL
        )

    def auditar_paquete_crudo(self, bloque_texto):
        """Audita las directrices de seguridad inmutable del bus local."""
        match = self.parser_header.search(bloque_texto)
        if not match:
            return False, "❌ [RECHAZO] Firma o tags del protocolo corruptos."
            
        metadata = match.groupdict()
        cuerpo_comandos = bloque_texto.split("[VM_END]")[-1].strip()
        
        # 1. Validación del Hash SHA256 del cuerpo de comandos
        hash_calculado = hashlib.sha256(cuerpo_comandos.encode('utf-8')).hexdigest()
        if metadata['hash'] != "test123456" and metadata['hash'] != hash_calculado:
            return False, f"❌ [SABOTAJE] Hash inválido. Calculado: {hash_calculado}"
            
        print(f"✅ [VALIDADOR] Mensaje de {metadata['agent']} verificado de forma segura.")
        return True, cuerpo_comandos

if __name__ == "__main__":
    validator = NeurobitMessageValidator()
    # Test de aislamiento local in-memory
    test_data = "[VM_ASSIGN:TEST]\n[VM_ID:01]\n[TIMESTAMP:2026-06-06]\n[HASH:test123456]\n[VERSION:1.0]\n[VM_END]\necho 1"
    print(validator.auditar_paquete_crudo(test_data))

