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
# NOTE: gunicorn.conf.py is now committed to the repo (gthread, 2x8 threads).
# Only overwrite if it does not exist (first deploy).
if [ ! -f "${APP_DIR}/gunicorn.conf.py" ]; then
cat > "${APP_DIR}/gunicorn.conf.py" << 'GUNICORN_EOF'
bind = "127.0.0.1:8000"
workers = 2
threads = 8
worker_class = "gthread"
timeout = 120
graceful_timeout = 30
keepalive = 5
max_requests = 500
max_requests_jitter = 50
accesslog = "/var/log/dip-practical/access.log"
errorlog = "/var/log/dip-practical/error.log"
loglevel = "info"
GUNICORN_EOF
fi

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
ExecStart=${VENV_DIR}/bin/gunicorn -c gunicorn.conf.py run:app
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable ${APP_NAME}
systemctl restart ${APP_NAME}

# --- Nginx (use the advanced config with microcaching from the repo) ---
echo "[*] Configuring Nginx..."
cp "${APP_DIR}/deploy/nginx-site.conf" /etc/nginx/sites-available/${APP_NAME}

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
