#!/usr/bin/env bash
# =============================================================================
# DIP Practical - Idempotent Zero-Intervention Deployment Script
# Target: Ubuntu 24.04 on GCP
# Result: Running Flask app on port 80 via Nginx reverse proxy
# =============================================================================
set -euo pipefail

APP_NAME="dip-practical"
APP_DIR="/opt/${APP_NAME}"
APP_USER="dipapp"
REPO_URL="https://github.com/divyamohan1993/dip-practical.git"
LOG_DIR="/var/log/${APP_NAME}"
VENV_DIR="${APP_DIR}/venv"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

echo "[$TIMESTAMP] === Starting ${APP_NAME} deployment ==="

# --- System packages ---
echo "[*] Updating system packages..."
export DEBIAN_FRONTEND=noninteractive
apt-get update -qq
apt-get upgrade -y -qq
apt-get install -y -qq \
    python3 python3-pip python3-venv \
    nginx git curl \
    libgl1-mesa-glx libglib2.0-0 \
    ufw

# --- App user ---
if ! id "${APP_USER}" &>/dev/null; then
    echo "[*] Creating application user: ${APP_USER}"
    useradd -r -m -s /bin/false "${APP_USER}"
fi

# --- Log directory ---
mkdir -p "${LOG_DIR}"
chown "${APP_USER}:${APP_USER}" "${LOG_DIR}"

# --- Clone/update repository ---
if [ -d "${APP_DIR}/.git" ]; then
    echo "[*] Updating existing repository..."
    cd "${APP_DIR}"
    git fetch origin
    git reset --hard origin/main
else
    echo "[*] Cloning repository..."
    rm -rf "${APP_DIR}"
    git clone "${REPO_URL}" "${APP_DIR}"
fi

cd "${APP_DIR}"
chown -R "${APP_USER}:${APP_USER}" "${APP_DIR}"

# --- Python virtual environment ---
echo "[*] Setting up Python virtual environment..."
if [ ! -d "${VENV_DIR}" ]; then
    python3 -m venv "${VENV_DIR}"
fi
"${VENV_DIR}/bin/pip" install --quiet --upgrade pip
"${VENV_DIR}/bin/pip" install --quiet -r requirements.txt

# --- Gunicorn config for production ---
cat > "${APP_DIR}/gunicorn.conf.py" << 'GUNICORN_EOF'
bind = "127.0.0.1:8000"
workers = 4
worker_class = "sync"
timeout = 120
keepalive = 5
accesslog = "/var/log/dip-practical/access.log"
errorlog = "/var/log/dip-practical/error.log"
loglevel = "info"
GUNICORN_EOF

# --- Systemd service ---
echo "[*] Configuring systemd service..."
cat > /etc/systemd/system/${APP_NAME}.service << EOF
[Unit]
Description=DIP Practical Web Application
After=network.target

[Service]
Type=simple
User=${APP_USER}
Group=${APP_USER}
WorkingDirectory=${APP_DIR}
Environment=PATH=${VENV_DIR}/bin:/usr/local/bin:/usr/bin:/bin
ExecStart=${VENV_DIR}/bin/gunicorn -c gunicorn.conf.py app.main:app
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable ${APP_NAME}
systemctl restart ${APP_NAME}

# --- Nginx ---
echo "[*] Configuring Nginx..."
cat > /etc/nginx/sites-available/${APP_NAME} << 'NGINX_EOF'
server {
    listen 80;
    server_name dip.dmj.one _;

    # Trust Cloudflare proxy headers
    set_real_ip_from 173.245.48.0/20;
    set_real_ip_from 103.21.244.0/22;
    set_real_ip_from 103.22.200.0/22;
    set_real_ip_from 103.31.4.0/22;
    set_real_ip_from 141.101.64.0/18;
    set_real_ip_from 108.162.192.0/18;
    set_real_ip_from 190.93.240.0/20;
    set_real_ip_from 188.114.96.0/20;
    set_real_ip_from 197.234.240.0/22;
    set_real_ip_from 198.41.128.0/17;
    set_real_ip_from 162.158.0.0/15;
    set_real_ip_from 104.16.0.0/13;
    set_real_ip_from 104.24.0.0/14;
    set_real_ip_from 172.64.0.0/13;
    set_real_ip_from 131.0.72.0/22;
    real_ip_header CF-Connecting-IP;

    client_max_body_size 10M;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 120s;
    }

    # Static files served directly by nginx for performance
    location /static/ {
        alias /opt/dip-practical/app/static/;
        expires 7d;
        add_header Cache-Control "public, immutable";
    }
}
NGINX_EOF

ln -sf /etc/nginx/sites-available/${APP_NAME} /etc/nginx/sites-enabled/${APP_NAME}
rm -f /etc/nginx/sites-enabled/default

nginx -t
systemctl enable nginx
systemctl restart nginx

# --- Firewall ---
echo "[*] Configuring firewall..."
ufw --force reset
ufw default deny incoming
ufw default allow outgoing
ufw allow 22/tcp
ufw allow 80/tcp
ufw --force enable

# --- Health check ---
echo "[*] Running health check..."
sleep 3
HEALTH=$(curl -sf http://localhost/health || echo "FAILED")
if echo "${HEALTH}" | grep -q "healthy"; then
    echo "[OK] Application is healthy!"
else
    echo "[WARN] Health check failed. Checking logs..."
    journalctl -u ${APP_NAME} --no-pager -n 20
fi

# --- Log rotation ---
cat > /etc/logrotate.d/${APP_NAME} << EOF
${LOG_DIR}/*.log {
    daily
    missingok
    rotate 14
    compress
    delaycompress
    notifempty
    create 0640 ${APP_USER} ${APP_USER}
    postrotate
        systemctl reload ${APP_NAME} > /dev/null 2>&1 || true
    endscript
}
EOF

EXTERNAL_IP=$(curl -sf http://metadata.google.internal/computeMetadata/v1/instance/network-interfaces/0/access-configs/0/external-ip -H "Metadata-Flavor: Google" || echo "unknown")
echo ""
echo "============================================="
echo " Deployment complete!"
echo " External IP: ${EXTERNAL_IP}"
echo " URL: http://dip.dmj.one"
echo " Health: http://${EXTERNAL_IP}/health"
echo " Logs: ${LOG_DIR}/"
echo "============================================="
echo "[$TIMESTAMP] === Deployment finished ==="
