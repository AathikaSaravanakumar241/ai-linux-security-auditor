# Production Deployment Checklist

Use this checklist before releasing the Security Auditor into production.

## 1. Database Configuration
- [ ] Database credentials are secure and updated from defaults (`postgres`/`postgres`).
- [ ] Connection pool parameters (`DB_POOL_SIZE` and `DB_MAX_OVERFLOW`) are configured based on target horizontal sizing.
- [ ] Named volume backup configurations are verified.
- [ ] Database is restricted and does not expose port `5432` to the public internet.

## 2. Secrets & Encryption
- [ ] `GEMINI_API_KEY` is active and loaded from a secure env environment, not coded into files.
- [ ] SSH target credentials are never persisted in the database logs (we only save IP, timestamps, raw results, and findings).
- [ ] CORS policies are restricted to target production domains (e.g. `CORS_ORIGINS=https://auditor.yourdomain.com`).

## 3. Network & OS Hardening
- [ ] HTTPS is enforced with a valid Let's Encrypt TLS certificate.
- [ ] HTTP requests automatically redirect to HTTPS (301 redirect).
- [ ] Root SSH login is disabled on target servers (`PermitRootLogin no`), verified by executing an audit.
- [ ] Port 22/SSH is hardened (either restricted by IP whitelist or set up with key-based authentication).

## 4. Monitoring & Cleanups
- [ ] Log levels are set to `WARNING` or `ERROR` in production to prevent log disk space exhaustions.
- [ ] Daily cron DB backups are running, and retention schedules are clearing backups older than 30 days.
- [ ] Docker container restart policies are set (`restart: always` or `restart: unless-stopped`).
- [ ] CPU and memory constraints are active inside compose declarations.
