# Production Checklist

E-Catalog Microservice'ni production'ga qo'yishdan oldin tekshirish ro'yxati.

## ✅ Tayyorlik Tekshiruvi

### 1. Environment Variables
Quyidagi environment variables sozlanganligini tekshiring:

```bash
# .env faylida yoki server environment'da
SECRET_KEY=your-strong-secret-key-here-min-50-chars
DEBUG=False
ALLOWED_HOSTS=your-domain.com,www.your-domain.com,api.your-domain.com
DATABASE_URL=postgresql://user:password@host:5432/ecatalog
CORS_ALLOWED_ORIGINS=https://your-frontend.com,https://another-service.com
```

### 2. Database
- [ ] PostgreSQL o'rnatilgan va ishlayapti
- [ ] Database yaratilgan
- [ ] User va password sozlangan
- [ ] Migrations qo'llangan
- [ ] Connection test qilingan

### 3. Security Settings
- [ ] `DEBUG=False` production'da
- [ ] `SECRET_KEY` kuchli va xavfsiz
- [ ] `ALLOWED_HOSTS` to'ldirilgan
- [ ] HTTPS sozlangan
- [ ] SSL sertifikat o'rnatilgan

### 4. CORS Configuration
- [ ] `CORS_ALLOWED_ORIGINS` boshqa servicelar manzillari bilan to'ldirilgan
- [ ] `CORS_ALLOW_CREDENTIALS=True` (agar kerak bo'lsa)
- [ ] `CORS_ALLOW_ALL_ORIGINS=False` production'da

### 5. Static va Media Files
- [ ] `python manage.py collectstatic` ishga tushirilgan
- [ ] Static files serve qilinadi
- [ ] Media files serve qilinadi
- [ ] WhiteNoise sozlangan (production uchun)

### 6. Server Configuration
- [ ] Gunicorn o'rnatilgan
- [ ] Systemd service yaratilgan
- [ ] Nginx sozlangan
- [ ] Firewall sozlangan
- [ ] Portlar ochilgan

### 7. Monitoring va Logging
- [ ] Logging sozlangan
- [ ] Log fayllar yaratilgan
- [ ] Monitoring tizimi sozlangan (ixtiyoriy)

## 🔗 Boshqa Servicelar bilan Integratsiya

### API Endpoint'lar
Barcha API endpoint'lar ishlayapti:
- ✅ `GET /api/v1/project/` - Project ro'yxati
- ✅ `POST /api/v1/project/` - Project yaratish
- ✅ `GET /api/v1/client/` - Client ro'yxati
- ✅ `POST /api/v1/client/` - Client yaratish
- ✅ `GET /api/v1/nomenklatura/` - Nomenklatura ro'yxati
- ✅ `POST /api/v1/nomenklatura/` - Nomenklatura yaratish

### Authentication
- ✅ JWT token authentication
- ✅ Token olish: `POST /api/token/`
- ✅ Token yangilash: `POST /api/token/refresh/`
- ✅ Token tekshirish: `POST /api/token/verify/`

### CORS Configuration
Boshqa servicelar bilan integratsiya uchun:

```python
# config/settings.py yoki .env
CORS_ALLOWED_ORIGINS = [
    "https://your-frontend-service.com",
    "https://your-api-gateway.com",
    "https://another-microservice.com",
]
```

### Rate Limiting
- Anonim foydalanuvchilar: 100 so'rov/soat
- Autentifikatsiya qilingan: 1000 so'rov/soat

## 🚀 Production'ga Qo'yish

### 1. Environment Variables Sozlash

```bash
# .env faylini yaratish
nano .env
```

`.env` faylida:
```env
SECRET_KEY=your-very-strong-secret-key-minimum-50-characters-long
DEBUG=False
ALLOWED_HOSTS=api.your-domain.com,your-domain.com
DATABASE_URL=postgresql://ecatalog_user:password@localhost:5432/ecatalog
CORS_ALLOWED_ORIGINS=https://frontend.your-domain.com,https://gateway.your-domain.com
```

### 2. Production Settings Ishlatish

```bash
# WSGI da production settings ishlatish
export DJANGO_SETTINGS_MODULE=config.settings_production

# Yoki gunicorn da
gunicorn config.wsgi:application --settings=config.settings_production
```

### 3. Docker orqali (Tavsiya etiladi)

```bash
# .env faylini yaratish
cp .env.example .env
# .env ni tahrirlash

# Docker Compose orqali
docker-compose up -d

# Loglarni tekshirish
docker-compose logs -f
```

## 🔍 Test Qilish

### 1. Health Check
```bash
curl https://your-domain.com/api/v1/
```

### 2. Authentication Test
```bash
# Token olish
curl -X POST https://your-domain.com/api/token/ \
  -H "Content-Type: application/json" \
  -d '{"username":"your_user","password":"your_password"}'

# Token bilan so'rov
curl https://your-domain.com/api/v1/project/ \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 3. CORS Test
Boshqa servicedan so'rov yuborish:
```javascript
fetch('https://your-domain.com/api/v1/project/', {
  method: 'GET',
  headers: {
    'Authorization': 'Bearer YOUR_TOKEN',
    'Content-Type': 'application/json',
  },
})
```

## ⚠️ Muhim Eslatmalar

1. **SECRET_KEY** - Production'da kuchli secret key ishlatish kerak
2. **DEBUG** - Production'da har doim `False` bo'lishi kerak
3. **ALLOWED_HOSTS** - Barcha domain'lar ro'yxatga kiritilishi kerak
4. **CORS** - Faqat ishonchli servicelar manzillari qo'shilishi kerak
5. **Database** - PostgreSQL ishlatish tavsiya etiladi (SQLite production uchun mos emas)
6. **HTTPS** - Production'da HTTPS ishlatish kerak
7. **Backup** - Database backup tizimi sozlanishi kerak

## 📞 Integratsiya Misollari

### Frontend Service
```javascript
// React, Vue, Angular va boshqalar
const API_URL = 'https://api.your-domain.com/api/v1/';

// Token olish
const response = await fetch(`${API_URL}../token/`, {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({username, password}),
});
const {access} = await response.json();

// API so'rov
const data = await fetch(`${API_URL}project/`, {
  headers: {
    'Authorization': `Bearer ${access}`,
    'Content-Type': 'application/json',
  },
});
```

### Backend Service (Python)
```python
import requests

API_URL = 'https://api.your-domain.com/api/v1/'

# Token olish
response = requests.post(f'{API_URL}../token/', json={
    'username': 'your_user',
    'password': 'your_password'
})
token = response.json()['access']

# API so'rov
headers = {'Authorization': f'Bearer {token}'}
projects = requests.get(f'{API_URL}project/', headers=headers).json()
```

## ✅ Tayyor!

Agar barcha checklist'lar bajarilgan bo'lsa, loyiha production'ga tayyor va boshqa servicelar bilan integratsiya qilish mumkin!

