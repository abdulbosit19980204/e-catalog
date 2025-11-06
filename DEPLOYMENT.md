# Deployment Qo'llanmasi

E-Catalog Microservice'ni production serverda ishga tushirish bo'yicha batafsil qo'llanma.

## 🐳 Docker orqali Deployment

### 1. Docker Image Build qilish

```bash
docker build -t ecatalog:latest .
```

### 2. Docker Compose orqali ishga tushirish

```bash
# .env faylini yaratish
cp .env.example .env
# .env faylini tahrirlash

# Docker Compose orqali ishga tushirish
docker-compose up -d

# Loglarni ko'rish
docker-compose logs -f

# To'xtatish
docker-compose down
```

### 3. Environment Variables

`.env` faylida quyidagilarni sozlang:

```env
SECRET_KEY=your-production-secret-key
DEBUG=False
ALLOWED_HOSTS=your-domain.com,www.your-domain.com
DATABASE_URL=postgresql://user:password@db:5432/ecatalog
CORS_ALLOWED_ORIGINS=https://your-frontend.com
```

## 🚀 Production Server Deployment

### 1. Server Talablari

- Ubuntu 20.04+ yoki boshqa Linux distributiv
- Python 3.11+
- PostgreSQL 15+
- Nginx
- Gunicorn

### 2. Server O'rnatish

```bash
# Python va pip o'rnatish
sudo apt update
sudo apt install python3.11 python3-pip python3-venv

# PostgreSQL o'rnatish
sudo apt install postgresql postgresql-contrib

# Nginx o'rnatish
sudo apt install nginx

# Git o'rnatish
sudo apt install git
```

### 3. Database Yaratish

```bash
sudo -u postgres psql
CREATE DATABASE ecatalog;
CREATE USER ecatalog_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE ecatalog TO ecatalog_user;
\q
```

### 4. Loyihani Serverga Yuklash

```bash
# Loyiha papkasiga o'tish
cd /var/www/
sudo git clone <repository-url> ecatalog
cd ecatalog

# Virtual environment yaratish
python3 -m venv venv
source venv/bin/activate

# Paketlarni o'rnatish
pip install -r requirements.txt
```

### 5. Environment Variables

```bash
# .env faylini yaratish
nano .env
```

`.env` faylida:
```env
SECRET_KEY=your-production-secret-key-here
DEBUG=False
ALLOWED_HOSTS=your-domain.com,www.your-domain.com
DATABASE_URL=postgresql://ecatalog_user:your_password@localhost:5432/ecatalog
CORS_ALLOWED_ORIGINS=https://your-frontend.com
```

### 6. Migrations va Static Files

```bash
# Migrations qo'llash
python manage.py migrate

# Superuser yaratish
python manage.py createsuperuser

# Static fayllar yig'ish
python manage.py collectstatic --noinput
```

### 7. Gunicorn Systemd Service

```bash
sudo nano /etc/systemd/system/ecatalog.service
```

Service fayli:
```ini
[Unit]
Description=E-Catalog Gunicorn daemon
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/ecatalog
Environment="PATH=/var/www/ecatalog/venv/bin"
ExecStart=/var/www/ecatalog/venv/bin/gunicorn \
    --workers 3 \
    --bind unix:/var/www/ecatalog/ecatalog.sock \
    config.wsgi:application

[Install]
WantedBy=multi-user.target
```

Service ishga tushirish:
```bash
sudo systemctl daemon-reload
sudo systemctl start ecatalog
sudo systemctl enable ecatalog
```

### 8. Nginx Konfiguratsiyasi

```bash
sudo nano /etc/nginx/sites-available/ecatalog
```

Nginx konfiguratsiyasi:
```nginx
server {
    listen 80;
    server_name your-domain.com www.your-domain.com;

    location /static/ {
        alias /var/www/ecatalog/staticfiles/;
    }

    location /media/ {
        alias /var/www/ecatalog/media/;
    }

    location / {
        include proxy_params;
        proxy_pass http://unix:/var/www/ecatalog/ecatalog.sock;
    }
}
```

Nginx'ni aktivlashtirish:
```bash
sudo ln -s /etc/nginx/sites-available/ecatalog /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### 9. SSL Sertifikat (Let's Encrypt)

```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com -d www.your-domain.com
```

## 🔄 CI/CD Pipeline

GitHub Actions orqali avtomatik test va build:

1. **Test** - Har bir push/PR da testlar ishga tushadi
2. **Build** - Main branch'ga push qilinganda Docker image build qilinadi

## 📊 Monitoring

### Loglar

```bash
# Gunicorn loglari
sudo journalctl -u ecatalog -f

# Nginx loglari
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log

# Django loglari
tail -f /var/www/ecatalog/logs/django.log
```

### Health Check

```bash
# API health check
curl http://your-domain.com/api/v1/

# Database connection
python manage.py dbshell
```

## 🔐 Xavfsizlik

1. **Secret Key** - Environment variable sifatida saqlang
2. **DEBUG=False** - Production'da DEBUG o'chirilgan bo'lishi kerak
3. **HTTPS** - SSL sertifikat o'rnatish
4. **Firewall** - Faqat kerakli portlarni ochish
5. **Database Backup** - Muntazam backup qilish

## 🔄 Yangilash

```bash
# Loyihani yangilash
cd /var/www/ecatalog
git pull origin main

# Virtual environment aktivlashtirish
source venv/bin/activate

# Paketlarni yangilash
pip install -r requirements.txt

# Migrations
python manage.py migrate

# Static files
python manage.py collectstatic --noinput

# Service qayta ishga tushirish
sudo systemctl restart ecatalog
```

## 📝 Checklist

- [ ] Server o'rnatilgan
- [ ] Database yaratilgan
- [ ] Environment variables sozlangan
- [ ] Migrations qo'llangan
- [ ] Static files yig'ilgan
- [ ] Gunicorn service ishga tushirilgan
- [ ] Nginx konfiguratsiyasi
- [ ] SSL sertifikat o'rnatilgan
- [ ] Firewall sozlangan
- [ ] Backup tizimi sozlangan
- [ ] Monitoring sozlangan

