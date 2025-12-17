# Environment Variables Setup Guide

Production uchun `.env` faylini sozlash bo'yicha qo'llanma.

## 📋 .env Faylini Yaratish

### 1. .env.example ni .env ga copy qiling:

```bash
# Linux/Mac
cp .env.example .env

# Windows
copy .env.example .env
```

### 2. .env faylini tahrirlang:

```bash
# Linux/Mac
nano .env

# Windows
notepad .env
```

## 🔑 Kerakli Environment Variables

### Backend (Django)

```env
# Django Secret Key - Production uchun yangi kuchli key yarating!
# Key yaratish: python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
SECRET_KEY=your-very-strong-secret-key-minimum-50-characters-long

# Debug Mode - Production'da har doim False!
DEBUG=False

# Django Settings Module
DJANGO_SETTINGS_MODULE=config.settings_production

# Allowed Hosts - server IP yoki domain nomlari (vergul bilan ajratilgan)
ALLOWED_HOSTS=178.218.200.120,192.168.0.129,your-domain.com,api.your-domain.com

# CSRF Trusted Origins - frontend va boshqa servicelar manzillari
CSRF_TRUSTED_ORIGINS=https://your-domain.com,https://frontend.your-domain.com,http://178.218.200.120:1596,http://192.168.0.129:8000

# PostgreSQL Database URL
# Format: postgresql://user:password@host:port/database
DATABASE_URL=postgresql://ecatalog:ecatalog123@db:5432/ecatalog

# Redis URL (Optional - agar Redis ishlatilsa)
REDIS_URL=redis://127.0.0.1:6379/1

# CORS Allowed Origins - Frontend va boshqa servicelar manzillari
CORS_ALLOWED_ORIGINS=https://your-frontend-domain.com,https://frontend.your-domain.com,http://178.218.200.120:1596,http://192.168.0.129:8000
```

### Frontend (React)

```env
# React App API URL - Frontend qaysi API'ga so'rov yuborishini ko'rsatadi
# Production uchun: https://api.your-domain.com/api/v1
REACT_APP_API_URL=http://178.218.200.120:1596/api/v1
```

### Docker PostgreSQL (Docker Compose uchun)

```env
POSTGRES_DB=ecatalog
POSTGRES_USER=ecatalog
POSTGRES_PASSWORD=ecatalog123
```

## 📝 To'liq .env Example

Quyidagi `.env.example` faylini `.env` ga copy qiling va qiymatlarni o'zgartiring:

```env
# ==============================================================================
# E-Catalog Microservice - Environment Variables
# ==============================================================================

# Django Backend Settings
SECRET_KEY=your-very-strong-secret-key-minimum-50-characters-long-change-this-in-production
DEBUG=False
DJANGO_SETTINGS_MODULE=config.settings_production

# Server Configuration
ALLOWED_HOSTS=178.218.200.120,192.168.0.129,your-domain.com,api.your-domain.com
CSRF_TRUSTED_ORIGINS=https://your-domain.com,https://frontend.your-domain.com,http://178.218.200.120:1596,http://192.168.0.129:8000

# Database Configuration
DATABASE_URL=postgresql://ecatalog:ecatalog123@db:5432/ecatalog

# Redis Configuration (Optional)
REDIS_URL=redis://127.0.0.1:6379/1

# CORS Configuration
CORS_ALLOWED_ORIGINS=https://your-frontend-domain.com,https://frontend.your-domain.com,http://178.218.200.120:1596,http://192.168.0.129:8000,http://localhost:3000

# Frontend Configuration
REACT_APP_API_URL=http://178.218.200.120:1596/api/v1

# Docker PostgreSQL Configuration
POSTGRES_DB=ecatalog
POSTGRES_USER=ecatalog
POSTGRES_PASSWORD=ecatalog123
```

## ⚠️ Muhim Eslatmalar

1. **.env fayli .gitignore da bo'lishi kerak** - Hech qachon gitga commit qilmang!
2. **SECRET_KEY** - Production'da yangi kuchli key yarating!
3. **DEBUG=False** - Production'da majburiy False bo'lishi kerak!
4. **DATABASE_URL** - Database parolni xavfsiz saqlang!
5. **ALLOWED_HOSTS** - Faqat ishonchli domain va IP'lar qo'shing!
6. **CORS_ALLOWED_ORIGINS** - Faqat kerakli frontend servicelar manzillarini qo'shing!

## 🔐 Secret Key Yaratish

Django secret key yaratish:

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

Yoki Django shell orqali:

```bash
python manage.py shell
>>> from django.core.management.utils import get_random_secret_key
>>> print(get_random_secret_key())
```

## 🚀 Production Deployment

Production'ga deploy qilishdan oldin:

1. `.env` faylini yarating va barcha qiymatlarni to'ldiring
2. `SECRET_KEY` ni yangi kuchli key bilan almashtiring
3. `DEBUG=False` ni tekshiring
4. `ALLOWED_HOSTS` ni to'g'ri domain'lar bilan to'ldiring
5. `DATABASE_URL` ni production database bilan almashtiring
6. `CORS_ALLOWED_ORIGINS` ni production frontend manzillari bilan to'ldiring

## 📚 Qo'shimcha Ma'lumot

- [Production Checklist](PRODUCTION_CHECKLIST.md)
- [Deployment Guide](DEPLOYMENT.md)
- [Django Settings Documentation](https://docs.djangoproject.com/en/stable/ref/settings/)





