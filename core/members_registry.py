#!/usr/bin/env python3
"""
Members Registry — CRUD para miembros del NEUROBIT_DEV_TEAM
Principio: Baja visual (move to inactive), nunca delete
"""
import json, yaml, os, shutil
from pathlib import Path
from datetime import datetime

class MembersRegistry:
    def __init__(self, workspace: str = None):
        self.workspace = Path(workspace) if workspace else Path.home() / "WORKSPACE_NEUROBIT_V0.2"
        self.members_dir = self.workspace / "data" / "members"
        self.inactive_dir = self.workspace / "data" / "inactive_members"
        self.index_file = self.members_dir / "INDEX_MEMBERS.jsonl"
        
        # Crear directorios si no existen
        self.members_dir.mkdir(parents=True, exist_ok=True)
        self.inactive_dir.mkdir(parents=True, exist_ok=True)
    
    def register_member(self, member_id: str, name: str, platform: str, role: str) -> dict:
        """Registrar nuevo miembro"""
        member_path = self.members_dir / member_id
        
        if member_path.exists():
            return {"success": False, "error": "Member already exists"}
        
        # Crear estructura
        member_path.mkdir(parents=True, exist_ok=True)
        (member_path / "logs").mkdir(exist_ok=True)
        (member_path / "tasks").mkdir(exist_ok=True)
        
        # profile.yaml
        profile = {
            "member_id": member_id,
            "name": name,
            "platform": platform,  # qwen_local, claude_vscode, etc.
            "role": role,  # asistente_tecnico, coordinador, etc.
            "status": "active",
            "registered_at": datetime.now().isoformat(),
            "last_task": None,
            "last_summary": None
        }
        
        with open(member_path / "profile.yaml", 'w', encoding='utf-8') as f:
            yaml.dump(profile, f, allow_unicode=True, default_flow_style=False)
        
        # status.json
        status = {
            "status": "active",
            "current_task": None,
            "last_activity": datetime.now().isoformat(),
            "tasks_completed": 0,
            "tasks_concluded": 0
        }
        
        with open(member_path / "status.json", 'w', encoding='utf-8') as f:
            json.dump(status, f, indent=2, ensure_ascii=False)
        
        # INDEX_MEMBERS.jsonl (append-only)
        index_entry = {
            "timestamp": datetime.now().isoformat(),
            "action": "REGISTER",
            "member_id": member_id,
            "name": name,
            "platform": platform,
            "role": role
        }
        
        with open(self.index_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(index_entry, ensure_ascii=False) + "\n")
        
        return {"success": True, "member_id": member_id, "path": str(member_path)}
    
    def deactivate_member(self, member_id: str, reason: str = "") -> dict:
        """Dar de baja visual (mover a inactive_members)"""
        source = self.members_dir / member_id
        dest = self.inactive_dir / member_id
        
        if not source.exists():
            return {"success": False, "error": "Member not found"}
        
        if dest.exists():
            return {"success": False, "error": "Member already inactive"}
        
        # Mover carpeta
        shutil.move(str(source), str(dest))
        
        # Actualizar profile.yaml
        profile_path = dest / "profile.yaml"
        with open(profile_path, 'r', encoding='utf-8') as f:
            profile = yaml.safe_load(f)
        
        profile["status"] = "inactive"
        profile["deactivated_at"] = datetime.now().isoformat()
        profile["deactivation_reason"] = reason
        
        with open(profile_path, 'w', encoding='utf-8') as f:
            yaml.dump(profile, f, allow_unicode=True, default_flow_style=False)
        
        # INDEX_MEMBERS.jsonl (append-only)
        index_entry = {
            "timestamp": datetime.now().isoformat(),
            "action": "DEACTIVATE",
            "member_id": member_id,
            "reason": reason
        }
        
        with open(self.index_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(index_entry, ensure_ascii=False) + "\n")
        
        return {"success": True, "member_id": member_id, "new_path": str(dest)}
    
    def get_member_status(self, member_id: str) -> dict:
        """Obtener estado de un miembro"""
        # Buscar en activos
        member_path = self.members_dir / member_id
        location = "active"
        
        if not member_path.exists():
            # Buscar en inactivos
            member_path = self.inactive_dir / member_id
            location = "inactive"
        
        if not member_path.exists():
            return {"success": False, "error": "Member not found"}
        
        # Leer profile y status
        with open(member_path / "profile.yaml", 'r', encoding='utf-8') as f:
            profile = yaml.safe_load(f)
        
        with open(member_path / "status.json", 'r', encoding='utf-8') as f:
            status = json.load(f)
        
        return {
            "success": True,
            "location": location,
            "profile": profile,
            "status": status,
            "path": str(member_path)
        }
    
    def list_members(self, active_only: bool = True) -> list:
        """Listar miembros"""
        members = []
        
        # Activos
        if active_only:
            for member_path in self.members_dir.iterdir():
                if member_path.is_dir() and not member_path.name.startswith('.'):
                    members.append({"member_id": member_path.name, "status": "active"})
        else:
            # Activos + Inactivos
            for member_path in self.members_dir.iterdir():
                if member_path.is_dir() and not member_path.name.startswith('.'):
                    members.append({"member_id": member_path.name, "status": "active"})
            
            for member_path in self.inactive_dir.iterdir():
                if member_path.is_dir() and not member_path.name.startswith('.'):
                    members.append({"member_id": member_path.name, "status": "inactive"})
        
        return members
    
    def create_daily_log(self, member_id: str, date: str = None) -> dict:
        """Crear carpeta diaria para logs"""
        if date is None:
            date = datetime.now().strftime("%Y-%m-%d")
        
        # Determinar ubicación (activo o inactivo)
        if (self.members_dir / member_id).exists():
            base_path = self.members_dir / member_id
        elif (self.inactive_dir / member_id).exists():
            base_path = self.inactive_dir / member_id
        else:
            return {"success": False, "error": "Member not found"}
        
        daily_path = base_path / "logs" / date
        daily_path.mkdir(parents=True, exist_ok=True)
        
        # Crear summary.md vacío (se llenará al final del día)
        summary_file = daily_path / "summary.md"
        if not summary_file.exists():
            with open(summary_file, 'w', encoding='utf-8') as f:
                f.write(f"# Resumen Diario — {date}\n\n")
                f.write(f"**Miembro:** {member_id}\n")
                f.write(f"**Fecha:** {date}\n")
                f.write(f"**Estado:** _Pendiente de resumen_\n\n")
                f.write("## Tareas Realizadas\n\n")
                f.write("## Resumen del Miembro\n\n")
                f.write("_Espacio para que el miembro escriba su resumen al final del día_\n")
        
        return {"success": True, "path": str(daily_path), "summary_file": str(summary_file)}
    
    def append_daily_summary(self, member_id: str, summary: str, date: str = None) -> dict:
        """Agregar resumen diario (append-only)"""
        if date is None:
            date = datetime.now().strftime("%Y-%m-%d")
        
        # Determinar ubicación
        if (self.members_dir / member_id).exists():
            base_path = self.members_dir / member_id
        elif (self.inactive_dir / member_id).exists():
            base_path = self.inactive_dir / member_id
        else:
            return {"success": False, "error": "Member not found"}
        
        summary_file = base_path / "logs" / date / "summary.md"
        
        if not summary_file.exists():
            return {"success": False, "error": "Daily log not found"}
        
        # Append al summary.md
        with open(summary_file, 'a', encoding='utf-8') as f:
            f.write(f"\n---\n**Resumen agregado:** {datetime.now().isoformat()}\n\n")
            f.write(summary)
            f.write("\n")
        
        # INDEX_MEMBERS.jsonl (append-only)
        index_entry = {
            "timestamp": datetime.now().isoformat(),
            "action": "DAILY_SUMMARY",
            "member_id": member_id,
            "date": date,
            "summary_length": len(summary)
        }
        
        with open(self.index_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(index_entry, ensure_ascii=False) + "\n")
        
        return {"success": True, "summary_file": str(summary_file)}