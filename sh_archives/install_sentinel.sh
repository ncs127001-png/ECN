#!/bin/bash
# install_sentinel.sh
# Instala y configura el Centinela del Workspace

echo "🔧 Instalando Workspace Sentinel..."

# 1. Instalar inotify-tools
echo "📦 Instalando inotify-tools..."
sudo apt update
sudo apt install -y inotify-tools

# 2. Configurar auditd (opcional pero recomendado)
if command -v auditctl &> /dev/null; then
    echo "🔒 Configurando auditd para auditoría forense..."
    sudo auditctl -w /home/gus/ECN/inbox -p warx -k workspace_inbox_monitor
    sudo auditctl -w /home/gus/ECN/core -p warx -k workspace_core_changes
    sudo auditctl -w /home/gus/ECN/modules -p warx -k workspace_modules_changes
fi

# 3. Crear servicio systemd
echo "📝 Creando servicio systemd..."
sudo tee /etc/systemd/system/sos-sentinel.service > /dev/null <<EOF
[Unit]
Description=SOS Workspace Sentinel - File Organization Daemon
After=network.target

[Service]
Type=simple
User=gus
WorkingDirectory=/home/gus/ECN
ExecStart=/bin/bash /home/gus/ECN/core/sos_workspace_sentinel.sh
Restart=always
RestartSec=10
StandardOutput=append:/home/gus/ECN/data/logs/sentinel_stdout.log
StandardError=append:/home/gus/ECN/data/logs/sentinel_stderr.log

[Install]
WantedBy=multi-user.target
EOF

# 4. Habilitar y iniciar servicio
echo "🚀 Habilitando servicio..."
sudo systemctl daemon-reload
sudo systemctl enable sos-sentinel.service
sudo systemctl start sos-sentinel.service

# 5. Verificar estado
echo ""
echo "✅ INSTALACIÓN COMPLETADA"
echo "========================="
sudo systemctl status sos-sentinel.service --no-pager

echo ""
echo "📋 Comandos útiles:"
echo "  Ver logs:      tail -f /home/gus/ECN/data/logs/sentinel_audit.log"
echo "  Ver estado:    systemctl status sos-sentinel"
echo "  Detener:       sudo systemctl stop sos-sentinel"
echo "  Reiniciar:     sudo systemctl restart sos-sentinel"
echo ""
echo "📂 Para probar: cp archivo.py /home/gus/ECN/inbox/"