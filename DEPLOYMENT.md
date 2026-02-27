# Production Deployment (Bare VM: Gunicorn + Nginx + MySQL)

This guide covers a minimal, repeatable deployment for this Django API on a Linux VM using systemd, Gunicorn, Nginx, and MySQL/MariaDB.

## 1) Prerequisites
- Ubuntu 22.04+ (or similar)
- Python 3.10+ (matches local venv)
- MySQL/MariaDB server reachable from the VM
- A domain or public IP (for Nginx server_name)
- Open ports: 22 (SSH), 80 (HTTP), 443 (HTTPS if using TLS)

## 2) Required environment variables
Set these in `/etc/environment` or a dedicated file sourced by systemd. Values shown are examples:

```
ENVIRONMENT=production
SECRET_KEY=change-me
DEBUG=False

DB_NAME_PROD=ndma
DB_USER_PROD=ndma
DB_PASSWORD_PROD=strong-password
DB_HOST_PROD=127.0.0.1
DB_PORT_PROD=3306

# (Optional) CORS / allowed hosts if you extend settings
ALLOWED_HOSTS=api.example.com
```

## 3) System packages
```
sudo apt update
sudo apt install -y python3-pip python3-venv build-essential libmysqlclient-dev nginx
```

## 4) App checkout & virtualenv
```
cd /opt
sudo mkdir -p ndma_api && sudo chown $USER:$USER ndma_api
cd ndma_api
git clone <your-repo-url> .
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

## 5) Django setup
```
source venv/bin/activate
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py createsuperuser --email_address superadmin@example.com
python manage.py seed_rbac   # optional if you rely on seeded roles/permissions
```

## 6) Gunicorn systemd service
Create `/etc/systemd/system/ndma_api.service`:
```
[Unit]
Description=Gunicorn service for ndma_api
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/opt/ndma_api
Environment="PATH=/opt/ndma_api/venv/bin" "ENVIRONMENT=production"
ExecStart=/opt/ndma_api/venv/bin/gunicorn --workers 3 --bind unix:/opt/ndma_api/ndma_api.sock config.wsgi:application
Restart=always

[Install]
WantedBy=multi-user.target
```
Enable & start:
```
sudo systemctl daemon-reload
sudo systemctl enable ndma_api
sudo systemctl start ndma_api
sudo systemctl status ndma_api
```

## 7) Nginx site
Create `/etc/nginx/sites-available/ndma_api`:
```
server {
    listen 80;
    server_name api.example.com;

    location /static/ {
        alias /opt/ndma_api/static/;
    }

    location / {
        include proxy_params;
        proxy_pass http://unix:/opt/ndma_api/ndma_api.sock;
    }
}
```
Enable & reload:
```
sudo ln -sf /etc/nginx/sites-available/ndma_api /etc/nginx/sites-enabled/ndma_api
sudo nginx -t
sudo systemctl reload nginx
```

## 8) TLS (optional but recommended)
Use Certbot with Nginx plugin once DNS points to the VM:
```
sudo apt install -y certbot python3-certbot-nginx
sudo certbot --nginx -d api.example.com
```

## 9) Zero-downtime deploys
- Pull latest code: `git pull`
- Install deps: `source venv/bin/activate && pip install -r requirements.txt`
- Run migrations: `python manage.py migrate`
- Collect static: `python manage.py collectstatic --noinput`
- Restart app: `sudo systemctl restart ndma_api`

## 10) Health checks & monitoring
- App status: `sudo systemctl status ndma_api`
- Gunicorn logs: `journalctl -u ndma_api -f`
- Nginx access/error logs: `/var/log/nginx/access.log`, `/var/log/nginx/error.log`
- DB connectivity: `mysql -h $DB_HOST_PROD -u $DB_USER_PROD -p$DB_PASSWORD_PROD $DB_NAME_PROD -e "select 1;"`

## 11) Production settings notes
- `DEBUG` must be `False`.
- `ALLOWED_HOSTS` should include your domain/IP. Extend `config/settings/base.py` or `prod.py` as needed.
- Rotate `SECRET_KEY` securely; never commit it.
- Ensure MySQL user has least-privilege to the target database.

## 12) Backup & rollback (outline)
- Nightly DB backups via `mysqldump` to remote storage.
- Keep last known-good release tagged; rollback by checking out the tag and restarting Gunicorn.

## 13) Smoke tests after deploy
- `GET /api/v1/auth/profile/` with a valid token -> 200.
- `POST /api/v1/auth/login/` -> returns access/refresh.
- `GET /api/v1/rbac/permissions/` as SUPER_ADMIN -> 200.
- `POST /api/v1/volunteer/create/` as STATE_ADMIN -> 201.
