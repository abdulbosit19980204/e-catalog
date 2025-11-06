# O'rnatish Qo'llanmasi

E-Catalog Microservice'ni o'rnatish va ishga tushirish bo'yicha batafsil qo'llanma.

## 📋 Talablar

Quyidagi dasturlar tizimda o'rnatilgan bo'lishi kerak:

- **Python 3.8+** - [Python.org](https://www.python.org/downloads/)
- **pip** - Python bilan birga keladi
- **Git** (ixtiyoriy) - Versiya boshqaruvi uchun

## 🚀 O'rnatish Qadamlari

### 1. Loyihani yuklab olish

```bash
# Git orqali (agar mavjud bo'lsa)
git clone <repository-url>
cd e-catalog

# Yoki loyiha papkasiga o'ting
cd d:\coding\Microservice\e-catalog
```

### 2. Virtual Environment yaratish

Virtual environment yaratish va aktivlashtirish:

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**Linux/Mac:**
```bash
python3 -m venv venv
source venv/bin/activate
```

Virtual environment muvaffaqiyatli aktivlashtirilganda, terminalda `(venv)` ko'rinadi.

### 3. Kerakli Paketlarni O'rnatish

```bash
pip install django==5.2.7
pip install djangorestframework==3.16.1
pip install django-ckeditor
pip install pillow
pip install django-imagekit
```

Yoki `requirements.txt` faylidan (agar mavjud bo'lsa):

```bash
pip install -r requirements.txt
```

### 4. Database Migrations

Ma'lumotlar bazasini yaratish va jadvallarni tayyorlash:

```bash
# Migrations yaratish
python manage.py makemigrations

# Migrations qo'llash
python manage.py migrate
```

### 5. Superuser Yaratish (Admin Panel uchun)

Admin panelga kirish uchun superuser yaratish:

```bash
python manage.py createsuperuser
```

Quyidagi ma'lumotlarni kiriting:
- Username
- Email (ixtiyoriy)
- Password
- Password confirmation

### 6. Static Fayllar Yig'ish (Production uchun)

Development rejimida bu qadam shart emas, lekin production uchun:

```bash
python manage.py collectstatic
```

### 7. Server Ishga Tushirish

Development server ishga tushirish:

```bash
python manage.py runserver
```

Server `http://localhost:8000` manzilida ishga tushadi.

## ✅ Tekshirish

Server muvaffaqiyatli ishga tushganini tekshirish:

1. **Brauzerda ochish**: `http://localhost:8000/api/v1/`
2. **Admin Panel**: `http://localhost:8000/admin/`
3. **API Root**: `http://localhost:8000/api/v1/` - Barcha endpoint'lar ro'yxati

## 🔧 Sozlash

### Settings Faylini O'zgartirish

`config/settings.py` faylida quyidagilarni o'zgartirishingiz mumkin:

```python
# DEBUG rejimi (production uchun False qiling)
DEBUG = True

# Ruxsat berilgan hostlar
ALLOWED_HOSTS = ['localhost', '127.0.0.1']

# Ma'lumotlar bazasi (default: SQLite)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Media fayllar papkasi
MEDIA_ROOT = BASE_DIR / 'media'
MEDIA_URL = '/media/'
```

### PostgreSQL O'rnatish (Production uchun)

Production uchun PostgreSQL ishlatish:

1. PostgreSQL o'rnatish
2. Database yaratish
3. `settings.py` ni yangilash:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'ecatalog',
        'USER': 'your_user',
        'PASSWORD': 'your_password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

4. `psycopg2` paketini o'rnatish:
```bash
pip install psycopg2-binary
```

## 🐛 Muammolarni Hal Qilish

### Virtual Environment Aktivlashtirilmagan

**Muammo**: `ModuleNotFoundError: No module named 'django'`

**Yechim**: Virtual environment aktivlashtirish:
```bash
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac
```

### Port Band

**Muammo**: `Error: That port is already in use`

**Yechim**: Boshqa port ishlatish:
```bash
python manage.py runserver 8001
```

### Migrations Xatosi

**Muammo**: Migration xatolari

**Yechim**: 
```bash
# Eski migrations o'chirish (ehtiyot bo'ling!)
# Keyin qayta yaratish
python manage.py makemigrations
python manage.py migrate
```

### Static Fayllar Muammosi

**Muammo**: Static fayllar ko'rinmaydi

**Yechim**: 
```bash
# Static papka yaratish
mkdir static

# Yoki settings.py dan STATICFILES_DIRS ni o'chirish
```

### Media Fayllar Ko'rinmaydi

**Muammo**: Yuklangan rasmlar ko'rinmaydi

**Yechim**: `config/urls.py` da media serve qo'shilganligini tekshiring:
```python
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
```

## 📦 Production Deployment

### Gunicorn O'rnatish

```bash
pip install gunicorn
```

### Nginx Konfiguratsiyasi

Nginx konfiguratsiyasi misoli:

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location /static/ {
        alias /path/to/e-catalog/static/;
    }

    location /media/ {
        alias /path/to/e-catalog/media/;
    }

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### Environment Variables

Production uchun secret key va boshqa ma'lumotlarni environment variables orqali saqlash:

```python
import os

SECRET_KEY = os.environ.get('SECRET_KEY')
DEBUG = os.environ.get('DEBUG', 'False') == 'True'
```

## 🔐 Xavfsizlik

Production uchun quyidagilarni amalga oshiring:

1. `DEBUG = False` qiling
2. `ALLOWED_HOSTS` ni to'ldiring
3. Secret key ni environment variable sifatida saqlang
4. HTTPS ishlatish
5. CSRF va XSS himoyasini tekshiring

## 📝 Keyingi Qadamlar

1. **Superuser yaratish** - Admin panelga kirish
2. **Ma'lumotlar qo'shish** - Admin panel orqali yoki API orqali
3. **API test qilish** - Postman yoki brauzer orqali
4. **Dokumentatsiyani o'rganish** - [API_DOCUMENTATION.md](API_DOCUMENTATION.md)

## 💡 Foydali Buyruqlar

```bash
# Server ishga tushirish
python manage.py runserver

# Migrations yaratish
python manage.py makemigrations

# Migrations qo'llash
python manage.py migrate

# Superuser yaratish
python manage.py createsuperuser

# Shell ochish (Python orqali ma'lumotlar bilan ishlash)
python manage.py shell

# Static fayllar yig'ish
python manage.py collectstatic

# Django versiyasini tekshirish
python manage.py version
```

## 📞 Yordam

Muammolar bo'lsa:
1. [README.md](README.md) ni ko'ring
2. [API_DOCUMENTATION.md](API_DOCUMENTATION.md) ni tekshiring
3. Django dokumentatsiyasiga murojaat qiling

