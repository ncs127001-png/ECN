# GUÍA RÁPIDA - ESTACIÓN CENTRAL NEUROBITRÓNICA

## 🚀 Inicio Rápido (5 minutos)

### Paso 1: Preparar Entorno
```bash
cd /home/gus/ECN
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
```

### Paso 2: Instalar Dependencias Mínimas
```bash
pip install flask flask-cors python-socketio psutil pyyaml
```

### Paso 3: Crear Directorios
```bash
mkdir -p data/fragments data/bitacora storage/backups
```

### Paso 4: Iniciar Servidor
```bash
python3 interface/ecn_central_server.py
```

### Paso 5: Abrir Dashboard
```
Navegador: http://localhost:5001/
```

---

## 📊 Interfaz Principal

### Dashboard Web (salon_debug_complete.html)

Características:
- **Panel Izquierdo:** Controles para iniciar/parar servicios
- **Panel Central:** Grid de 46 componentes con estado en vivo
- **Panel Derecho:** Logs y estadísticas del sistema
- **Footer:** Controles de emergencia y exportación

### Componentes Destacados

```
🟢 ONLINE (Verde)     - Servicio activo
🔴 OFFLINE (Rojo)     - Servicio parado
🟡 LOADING (Amarillo) - Servicio en transición
```

---

## 🔧 Operaciones Básicas

### Iniciar un Servicio
```bash
# Vía API
curl -X POST http://localhost:5001/api/control/start/HID_Adapter

# Vía Dashboard
Clic en [▶] junto al componente
```

### Detener un Servicio
```bash
# Vía API
curl -X POST http://localhost:5001/api/control/stop/HID_Adapter

# Vía Dashboard
Clic en [⏹] junto al componente
```

### Ver Estado Actual
```bash
curl http://localhost:5001/api/status | jq .
```

### Ver Logs
```bash
curl http://localhost:5001/api/logs?limit=50 | jq .
```

### Health Check
```bash
curl http://localhost:5001/api/health | jq .
```

---

## 📋 Archivos Principales

| Archivo | Función |
|---------|---------|
| `ECN_state.txt` | Estado global del sistema |
| `interface/salon_debug_complete.html` | Dashboard web |
| `interface/ecn_central_server.py` | Servidor Flask |
| `docs/INFORME_ECN_v0.1.md` | Documentación técnica |
| `data/bitacora/bitacora_eva.jsonl` | Logs del sistema |
| `data/fragments/` | Almacenamiento de fragmentos |
| `storage/backups/` | Copias de seguridad |

---

## 🛠️ Troubleshooting

### Problema: "Port 5001 already in use"
```bash
# Liberar puerto
lsof -i :5001
kill -9 <PID>
```

### Problema: "Module not found"
```bash
# Verificar venv está activado
source .venv/bin/activate

# Reinstalar dependencias
pip install -r requirements.txt
```

### Problema: Dashboard no carga
```bash
# Verificar servidor está corriendo
curl http://localhost:5001/
# Debe retornar HTML del dashboard
```

### Problema: API no responde
```bash
# Ver logs del servidor
# Terminal donde corre ecn_central_server.py

# Reiniciar servidor
# Ctrl+C y ejecutar nuevamente
```

---

## 📚 Documentación Completa

Archivo: `/home/gus/ECN/docs/INFORME_ECN_v0.1.md`

Contiene:
- Arquitectura completa del sistema
- Diagrama de dependencias
- Descripción de 46 componentes
- Flujos de datos
- Casos de uso
- Capacidades de escalabilidad

---

## 🎯 Casos de Uso Comunes

### Monitorear Sesión de Desarrollo
```bash
# 1. Iniciar HID Adapter
curl -X POST http://localhost:5001/api/control/start/HID_Adapter

# 2. Iniciar Keylogger
curl -X POST http://localhost:5001/api/control/start/Neurobit_Keylogger

# 3. Ver logs en vivo
watch 'curl -s http://localhost:5001/api/logs?limit=10 | jq .'

# 4. Exportar sesión
curl http://localhost:5001/api/logs > sesion_$(date +%Y%m%d_%H%M%S).json
```

### Análisis de Sistema
```bash
# 1. Ejecutar health check
curl http://localhost:5001/api/health | jq .

# 2. Ver componentes activos
curl http://localhost:5001/api/components | jq '.components | to_entries[] | select(.value.status == "online")'

# 3. Monitorear en tiempo real
watch -n 1 'curl -s http://localhost:5001/api/system/info | jq .cpu_percent'
```

### Backup y Recuperación
```bash
# Hacer backup
python3 core/sos_file_manager.py --backup

# Listar backups
python3 core/sos_file_manager.py --list-backups

# Restaurar desde backup
python3 core/sos_file_manager.py --restore <backup_id>
```

---

## 🔐 Seguridad Local

El sistema funciona en **soberanía local**:
- ✓ Todos los datos están en `/home/gus/ECN/`
- ✓ No se conecta a internet
- ✓ Auditoría completa en `bitacora_eva.jsonl`
- ✓ Control total del usuario

---

## 📞 Soporte

En caso de problemas:
1. Revisar archivo de logs: `data/bitacora/bitacora_eva.jsonl`
2. Ejecutar health check: `curl http://localhost:5001/api/health`
3. Ver documentación: `docs/INFORME_ECN_v0.1.md`
4. Revisar estado: `cat ECN_state.txt`

---

## 🚀 Próximos Pasos

1. **Explorar Dashboard** - Familiarse con la interfaz
2. **Leer Documentación** - Entender arquitectura completa
3. **Activar Componentes** - Comenzar a monitorear
4. **Personalizar** - Agregar nuevos componentes según necesidad

---

**Última Actualización:** 2026-07-14  
**Versión:** 0.1-SOBERANO-LOCAL  
**Estado:** Operacional
