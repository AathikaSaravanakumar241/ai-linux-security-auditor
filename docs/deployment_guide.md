# Deployment Guide — AI Linux Security Auditor

This guide outlines deployment procedures for containerized production systems.

## System Architecture

```mermaid
graph TD
    Client[Web Browser] -->|HTTPS / Port 443| Nginx[Nginx Reverse Proxy]
    Nginx -->|Static Assets| SPA[React SPA Bundle]
    Nginx -->|API Requests /api/*| Backend[FastAPI App Container]
    Backend -->|SQL / Port 5432| DB[(PostgreSQL Database)]
    Backend -->|SSH / Port 22| Target[Target Linux Server]
    Backend -->|HTTPS / API Call| Gemini[Google Gemini API]
```

---

## Infrastructure Requirements

- **Processor**: 2 vCPUs or higher.
- **Memory**: 4 GB RAM.
- **Storage**: 20 GB SSD.
- **OS**: Ubuntu 22.04 LTS (recommended) or Debian 12.
- **Runtime**: Docker Engine 24.0+ and Docker Compose v2.20+.

---

## Production Environments Configuration

### 1. Environment Secrets Setup
Create a secure `.env` file inside your server deployment directory. Never commit secrets to code repositories.

```ini
# --- Postgres ---
POSTGRES_USER=auditor_admin
POSTGRES_PASSWORD=SECURE_RANDOM_PASSWORD_HERE
POSTGRES_DB=linux_audit_prod

# --- Backend Application ---
DATABASE_URL=postgresql://auditor_admin:SECURE_RANDOM_PASSWORD_HERE@postgres:5432/linux_audit_prod
GEMINI_API_KEY=YOUR_PRODUCTION_GEMINI_API_KEY
GEMINI_MODEL=gemini-2.0-flash
LOG_LEVEL=WARNING
CORS_ORIGINS=https://auditor.yourdomain.com

# --- Frontend Application ---
VITE_API_URL=https://auditor.yourdomain.com/api
```

---

### 2. HTTPS/SSL Certificate Setup
We recommend using **Let's Encrypt** with `certbot` to manage automated SSL certificates.

On the host machine, run:
```bash
sudo apt-get update
sudo apt-get install certbot
sudo certbot certonly --standalone -d auditor.yourdomain.com
```

This generates certificates in `/etc/letsencrypt/live/auditor.yourdomain.com/`. Mount these directories inside the Nginx container to enable HTTPS.

---

### 3. Nginx Server Configuration (`nginx.conf`)
Deploy Nginx as a reverse proxy listening on ports 80 and 443. It will redirect HTTP traffic to HTTPS, serve React static bundles, and proxy `/api/*` traffic to the FastAPI application.

```nginx
# Redirect HTTP to HTTPS
server {
    listen 80;
    server_name auditor.yourdomain.com;
    return 301 https://$host$request_uri;
}

# HTTPS Server block
server {
    listen 443 ssl http2;
    server_name auditor.yourdomain.com;

    ssl_certificate /etc/letsencrypt/live/auditor.yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/auditor.yourdomain.com/privkey.pem;

    # SSL security optimization settings
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;

    # Serve built static files
    location / {
        root /usr/share/nginx/html;
        index index.html index.htm;
        try_files $uri $uri/ /index.html;
    }

    # Proxy API calls to the backend service
    location /api/ {
        proxy_pass http://backend:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

---

## Database Backups & Retention

To safeguard audit history, schedule daily automated backups of the PostgreSQL database.

Create a cron job script `/opt/scripts/backup_db.sh`:
```bash
#!/bin/bash
BACKUP_DIR="/var/backups/postgres"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
FILENAME="$BACKUP_DIR/audit_db_$TIMESTAMP.sql.gz"

mkdir -p "$BACKUP_DIR"
docker exec -t linux_audit_db pg_dump -U postgres -d linux_audit | gzip > "$FILENAME"

# Delete backups older than 30 days
find "$BACKUP_DIR" -type f -name "*.sql.gz" -mtime +30 -delete
```

Schedule it to run daily at midnight via crontab:
```cron
0 0 * * * /bin/bash /opt/scripts/backup_db.sh
```

---

## Horizontal Scaling & Optimization

- **Database Connection Pooling**: Ensure `DB_POOL_SIZE` is adjusted when scaling the backend horizontally to prevent database connection exhaustion.
- **Managed Services**: For larger enterprise usage, replace the self-hosted Postgres service with managed database instances like AWS RDS or Google Cloud SQL, and use a dedicated secrets manager (e.g. AWS Secrets Manager) for API keys.
