#!/usr/bin/env python3
"""
Tests básicos para MembersRegistry
"""
import sys
import json
import tempfile
from pathlib import Path
from datetime import datetime

# Agregar core al path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.members_registry import MembersRegistry


def test_register_member():
    """Test: registrar un nuevo miembro"""
    print("\n=== TEST: register_member ===")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        registry = MembersRegistry(workspace=tmpdir)
        
        result = registry.register_member(
            member_id="qwen_local_01",
            name="Qwen Local",
            platform="ollama",
            role="asistente_tecnico"
        )
        
        assert result["success"] == True, f"Falló: {result}"
        assert result["member_id"] == "qwen_local_01"
        
        # Verificar que la carpeta existe
        member_path = Path(tmpdir) / "data" / "members" / "qwen_local_01"
        assert member_path.exists(), "Carpeta del miembro no fue creada"
        
        # Verificar que profile.yaml existe
        assert (member_path / "profile.yaml").exists(), "profile.yaml no existe"
        
        # Verificar que status.json existe
        assert (member_path / "status.json").exists(), "status.json no existe"
        
        # Verificar que se registró en INDEX_MEMBERS.jsonl
        index_file = Path(tmpdir) / "data" / "members" / "INDEX_MEMBERS.jsonl"
        with open(index_file, 'r') as f:
            first_line = f.readline()
            index_entry = json.loads(first_line)
            assert index_entry["action"] == "REGISTER"
            assert index_entry["member_id"] == "qwen_local_01"
        
        print("✅ Miembro registrado correctamente")
        print(f"   Carpeta: {member_path}")
        print(f"   Archivos: profile.yaml, status.json, logs/, tasks/")
        print(f"   INDEX_MEMBERS.jsonl actualizado")


def test_get_member_status():
    """Test: obtener estado de un miembro"""
    print("\n=== TEST: get_member_status ===")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        registry = MembersRegistry(workspace=tmpdir)
        
        # Registrar miembro
        registry.register_member("claude_vscode", "Claude VSCode", "vscode", "coordinador")
        
        # Obtener estado
        result = registry.get_member_status("claude_vscode")
        
        assert result["success"] == True
        assert result["location"] == "active"
        assert result["profile"]["member_id"] == "claude_vscode"
        assert result["profile"]["status"] == "active"
        assert result["status"]["status"] == "active"
        
        print("✅ Estado del miembro obtenido correctamente")
        print(f"   Miembro: {result['profile']['name']}")
        print(f"   Plataforma: {result['profile']['platform']}")
        print(f"   Rol: {result['profile']['role']}")


def test_list_members():
    """Test: listar miembros"""
    print("\n=== TEST: list_members ===")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        registry = MembersRegistry(workspace=tmpdir)
        
        # Registrar varios miembros
        registry.register_member("qwen_local_01", "Qwen Local", "ollama", "asistente_tecnico")
        registry.register_member("claude_vscode", "Claude VSCode", "vscode", "coordinador")
        registry.register_member("gpt4_cloud", "GPT-4 Cloud", "openai", "revisor")
        
        # Listar activos
        members = registry.list_members(active_only=True)
        
        assert len(members) == 3, f"Se esperaban 3 miembros, se obtuvieron {len(members)}"
        assert all(m["status"] == "active" for m in members)
        
        print(f"✅ {len(members)} miembros listados correctamente")
        for m in members:
            print(f"   - {m['member_id']} ({m['status']})")


def test_deactivate_member():
    """Test: dar de baja visual a un miembro"""
    print("\n=== TEST: deactivate_member ===")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        registry = MembersRegistry(workspace=tmpdir)
        
        # Registrar miembro
        registry.register_member("test_member", "Test Member", "test", "asistente")
        
        # Verificar que está activo
        result = registry.get_member_status("test_member")
        assert result["location"] == "active"
        
        # Dar de baja
        result = registry.deactivate_member("test_member", reason="Cambio de equipo")
        assert result["success"] == True
        
        # Verificar que está inactivo
        result = registry.get_member_status("test_member")
        assert result["location"] == "inactive"
        assert result["profile"]["status"] == "inactive"
        
        # Verificar que se registró en INDEX_MEMBERS.jsonl
        index_file = Path(tmpdir) / "data" / "members" / "INDEX_MEMBERS.jsonl"
        with open(index_file, 'r') as f:
            lines = f.readlines()
            deactivate_entry = json.loads(lines[-1])
            assert deactivate_entry["action"] == "DEACTIVATE"
        
        print("✅ Miembro dado de baja correctamente (baja visual)")
        print(f"   Carpeta movida a: inactive_members/")
        print(f"   Status actualizado a: inactive")


def test_daily_log():
    """Test: crear y agregar resumen diario"""
    print("\n=== TEST: create_daily_log + append_daily_summary ===")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        registry = MembersRegistry(workspace=tmpdir)
        
        # Registrar miembro
        registry.register_member("member_01", "Member 01", "test", "asistente")
        
        # Crear log diario
        date = "2026-04-28"
        result = registry.create_daily_log("member_01", date=date)
        assert result["success"] == True
        
        summary_file = Path(result["summary_file"])
        assert summary_file.exists()
        
        print(f"✅ Log diario creado: {date}")
        
        # Agregar resumen
        result = registry.append_daily_summary(
            "member_01",
            summary="- Completada tarea 1\n- Iniciada tarea 2",
            date=date
        )
        assert result["success"] == True
        
        # Verificar que se agregó
        with open(summary_file, 'r') as f:
            content = f.read()
            assert "Completada tarea 1" in content
        
        print(f"✅ Resumen diario agregado correctamente")
        print(f"   Archivo: {summary_file}")


def run_all_tests():
    """Ejecutar todos los tests"""
    print("\n" + "="*60)
    print("🧪 TESTS PARA MembersRegistry")
    print("="*60)
    
    tests = [
        test_register_member,
        test_get_member_status,
        test_list_members,
        test_deactivate_member,
        test_daily_log
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            test()
            passed += 1
        except Exception as e:
            failed += 1
            print(f"❌ FALLÓ: {test.__name__}")
            print(f"   Error: {e}")
    
    print("\n" + "="*60)
    print(f"📊 RESULTADOS: {passed} passed, {failed} failed")
    print("="*60 + "\n")
    
    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
