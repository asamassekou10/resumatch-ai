#!/bin/bash
# =============================================================================
# VPS Initial Setup Script for Hetzner CX22 (Ubuntu 24.04 LTS)
# Run as root on a fresh server: bash vps-setup.sh
# =============================================================================

set -euo pipefail

DEPLOY_USER="deploy"
SSH_PORT=22

echo "=== Starting VPS setup ==="

# --- System updates ---
echo "[1/7] Updating system packages..."
apt-get update && apt-get upgrade -y
apt-get install -y curl wget git ufw fail2ban apt-transport-https ca-certificates gnupg lsb-release

# --- Create deploy user ---
echo "[2/7] Creating deploy user..."
if ! id "$DEPLOY_USER" &>/dev/null; then
    adduser --disabled-password --gecos "" "$DEPLOY_USER"
    usermod -aG sudo "$DEPLOY_USER"
    # Allow sudo without password for deploy user
    echo "$DEPLOY_USER ALL=(ALL) NOPASSWD:ALL" > /etc/sudoers.d/$DEPLOY_USER

    # Copy SSH keys from root to deploy user
    mkdir -p /home/$DEPLOY_USER/.ssh
    cp /root/.ssh/authorized_keys /home/$DEPLOY_USER/.ssh/
    chown -R $DEPLOY_USER:$DEPLOY_USER /home/$DEPLOY_USER/.ssh
    chmod 700 /home/$DEPLOY_USER/.ssh
    chmod 600 /home/$DEPLOY_USER/.ssh/authorized_keys
    echo "Deploy user created with SSH access."
else
    echo "Deploy user already exists, skipping."
fi

# --- SSH hardening ---
echo "[3/7] Hardening SSH..."
sed -i 's/#PermitRootLogin yes/PermitRootLogin no/' /etc/ssh/sshd_config
sed -i 's/PermitRootLogin yes/PermitRootLogin no/' /etc/ssh/sshd_config
sed -i 's/#PasswordAuthentication yes/PasswordAuthentication no/' /etc/ssh/sshd_config
sed -i 's/PasswordAuthentication yes/PasswordAuthentication no/' /etc/ssh/sshd_config
systemctl restart sshd

# --- Firewall ---
echo "[4/7] Configuring UFW firewall..."
ufw default deny incoming
ufw default allow outgoing
ufw allow $SSH_PORT/tcp
ufw allow 80/tcp
ufw allow 443/tcp
ufw --force enable

# --- Fail2ban ---
echo "[5/7] Configuring fail2ban..."
cat > /etc/fail2ban/jail.local <<'JAILEOF'
[DEFAULT]
bantime = 3600
findtime = 600
maxretry = 5

[sshd]
enabled = true
port = ssh
filter = sshd
logpath = /var/log/auth.log
maxretry = 3
JAILEOF
systemctl enable fail2ban
systemctl restart fail2ban

# --- Install Docker ---
echo "[6/7] Installing Docker..."
if ! command -v docker &>/dev/null; then
    curl -fsSL https://get.docker.com | sh
    usermod -aG docker $DEPLOY_USER
    systemctl enable docker
    systemctl start docker
    echo "Docker installed."
else
    echo "Docker already installed, skipping."
fi

# --- Install Docker Compose (plugin) ---
if ! docker compose version &>/dev/null; then
    apt-get install -y docker-compose-plugin
    echo "Docker Compose plugin installed."
else
    echo "Docker Compose already installed, skipping."
fi

# --- Setup app directory ---
echo "[7/7] Setting up application directory..."
APP_DIR="/home/$DEPLOY_USER/app"
mkdir -p $APP_DIR
chown -R $DEPLOY_USER:$DEPLOY_USER $APP_DIR

# --- Swap file (important for 4GB RAM VPS) ---
echo "Setting up 2GB swap file..."
if [ ! -f /swapfile ]; then
    fallocate -l 2G /swapfile
    chmod 600 /swapfile
    mkswap /swapfile
    swapon /swapfile
    echo '/swapfile none swap sw 0 0' >> /etc/fstab
    # Optimize swap usage
    echo 'vm.swappiness=10' >> /etc/sysctl.conf
    sysctl -p
    echo "Swap configured."
else
    echo "Swap already exists, skipping."
fi

echo ""
echo "=== VPS setup complete! ==="
echo ""
echo "Next steps:"
echo "  1. Log in as deploy user:  ssh $DEPLOY_USER@<your-server-ip>"
echo "  2. Clone your repo:        git clone <your-repo-url> ~/app"
echo "  3. Copy .env.production:    cp .env.production ~/app/.env.production"
echo "  4. Start the app:           cd ~/app && docker compose -f docker-compose.prod.yml up -d"
echo ""
echo "IMPORTANT: Root SSH login is now DISABLED. Use the '$DEPLOY_USER' user."
