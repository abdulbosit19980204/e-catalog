#!/usr/bin/env python
"""
.env.example faylini yaratish uchun script
"""
import os

env_example_content = """# ==============================================================================
# E-Catalog Microservice - Environment Variables Template
# ==============================================================================
# Bu fayl production uchun environment variable'larni ko'rsatadi.
# .env.example ni .env ga copy qiling va qiymatlarni o'zgartiring:
# Linux/Mac: cp .env.example .env
# Windows: copy .env.example .env
# ==============================================================================

# ==============================================================================
# Django Backend Settings
# ==============================================================================

# Django Secret Key - juda muhim! Hech qachon gitga commit qilmang!
# Kuchli secret key yaratish: python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
SECRET_KEY=your-very-strong-secret-key-minimum-50-characters-long-change-this-in-production

# Debug Mode - Production'da har doim False bo'lishi kerak!
DEBUG=False

# Django Settings Module - Production'da settings_production ishlatiladi
DJANGO_SETTINGS_MODULE=config.settings_production

# ==============================================================================
# Server Configuration
# ==============================================================================

# Allowed Hosts - server IP yoki domain nomlari (vergul bilan ajratilgan)
ALLOWED_HOSTS=178.218.200.120,192.168.0.129,your-domain.com,api.your-domain.com

# CSRF Trusted Origins - frontend va boshqa servicelar manzillari
CSRF_TRUSTED_ORIGINS=https://your-domain.com,https://frontend.your-domain.com,http://178.218.200.120:1596,http://192.168.0.129:8000

# ==============================================================================
# Database Configuration
# ==============================================================================

# PostgreSQL Database URL
# Format: postgresql://user:password@host:port/database
# Docker compose uchun: postgresql://ecatalog:password@db:5432/ecatalog
# Tashqi PostgreSQL uchun: postgresql://user:password@localhost:5432/ecatalog
DATABASE_URL=postgresql://ecatalog:ecatalog123@db:5432/ecatalog

# ==============================================================================
# Redis Configuration (Optional - agar Redis ishlatilsa)
# ==============================================================================

# Redis URL - Cache uchun
# Format: redis://host:port/db_number
REDIS_URL=redis://127.0.0.1:6379/1

# ==============================================================================
# CORS Configuration
# ==============================================================================

# CORS Allowed Origins - Frontend va boshqa servicelar manzillari
CORS_ALLOWED_ORIGINS=https://your-frontend-domain.com,https://frontend.your-domain.com,http://178.218.200.120:1596,http://192.168.0.129:8000,http://localhost:3000

# ==============================================================================
# Frontend Configuration (React)
# ==============================================================================

# React App API URL - Frontend qaysi API'ga so'rov yuborishini ko'rsatadi
# Production uchun: https://api.your-domain.com/api/v1
# Development uchun: http://localhost:8000/api/v1
REACT_APP_API_URL=http://178.218.200.120:1596/api/v1

# ==============================================================================
# Docker PostgreSQL Configuration (Docker Compose uchun)
# ==============================================================================

# PostgreSQL Database Name
POSTGRES_DB=ecatalog

# PostgreSQL User
POSTGRES_USER=ecatalog

# PostgreSQL Password
POSTGRES_PASSWORD=ecatalog123

# ==============================================================================
# Notes
# ==============================================================================
# 1. .env fayli .gitignore da bo'lishi kerak va hech qachon gitga commit qilinmasligi kerak!
# 2. Production'da SECRET_KEY, DATABASE_URL, POSTGRES_PASSWORD kabi sezgirliklarni xavfsiz saqlang!
# 3. Barcha URL va domain nomlarini o'zingizga mos qilib o'zgartiring!
# 4. DEBUG=False production'da majburiy!
# ==============================================================================
"""

if __name__ == "__main__":
    file_path = ".env.example"
    
    # Non-interactive mode - agar fayl mavjud bo'lsa, ustiga yozadi
    overwrite = True
    
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(env_example_content)
        print(f"✅ {file_path} fayli muvaffaqiyatli yaratildi!")
        print(f"\nKeyingi qadam:")
        print(f"1. {file_path} ni .env ga copy qiling:")
        print(f"   Linux/Mac: cp {file_path} .env")
        print(f"   Windows: copy {file_path} .env")
        print(f"2. .env faylini tahrirlang va qiymatlarni o'zgartiring")
        print(f"3. Batafsil ma'lumot: ENV_SETUP.md faylini o'qing")
    except Exception as e:
        print(f"❌ Xatolik: {e}")
        exit(1)

