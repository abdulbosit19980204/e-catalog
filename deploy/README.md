# E-Catalog Deployment Guide

Ushbu loyihani Production serverda (Linux/Ubuntu) ishga tushirish bo'yicha qo'llanma.

## 🏗️ Tizim arxitekturasi

- **Frontend:** React (3000 -> 1563 portda Nginx orqali)
- **Backend:** Django (1596 portda Gunicorn/Daphne orqali)
- **Server:** Nginx (Proxy sifatida)
- **Ma'lumotlar bazasi:** SQLite (WAL mode yoqilgan)
- **Kesh/Tasklar:** Redis

---

## 🚀 O'rnatish qadamlari

### 1. Nginx Sozlamalari

Nginx konfiguratsiya fayllari `deploy/nginx/` papkasida joylashgan. Ularni serverga nusxalash:

```bash
# Backend uchun
sudo cp deploy/nginx/backend.conf /etc/nginx/sites-available/e-catalog-backend
sudo ln -s /etc/nginx/sites-available/e-catalog-backend /etc/nginx/sites-enabled/

# Frontend uchun
sudo cp deploy/nginx/frontend.conf /etc/nginx/sites-available/e-catalog-frontend
sudo ln -s /etc/nginx/sites-available/e-catalog-frontend /etc/nginx/sites-enabled/

# Tekshirish va qayta yuklash
sudo nginx -t
sudo systemctl restart nginx
```

### 2. Frontend Build

Frontend-ni Production uchun tayyorlash:

```bash
cd frontend
npm install
npm run build
```
*Eslatma: Nginx `frontend/build` papkasidagi fayllarni 1563-portda xizmat ko'rsatadi.*

### 3. Backend Sozlash

```bash
# Virtual muhitni yaratish
python -m venv venv
source venv/bin/activate

# Kutubxonalarni o'rnatish
pip install -r requirements.txt

# Statik fayllarni yig'ish
python manage.py collectstatic --noinput

# Gunicorn-ni ishga tushirish (unix socket orqali)
gunicorn config.wsgi:application --bind unix:/run/gunicorn.sock
```

---

## 🔒 Xavfsizlik va CORS

Frontend **1563** portda ishlashi uchun `config/settings.py` faylida quyidagi originlar ruxsat etilgan:
- `http://178.218.200.120:1563`
- `http://localhost:1563`

Agar IP-manzil o'zgarsa, ushbu fayldagi `CORS_ALLOWED_ORIGINS` va `CSRF_TRUSTED_ORIGINS` ro'yxatlarini yangilang.

## 🛠️ Muammolarni hal qilish

- **Port bandligi:** Agar `nginx -t`da xatolik chiqsa, port boshqa dastur (masalan `npm start`) tomonidan band qilinmaganini tekshiring: `sudo lsof -i :1563`
- **404 xatosi:** Sahifa yangilanganda 404 chiqsa, Nginx-dagi `try_files $uri $uri/ /index.html;` qatori borligini tekshiring.
- **Rasm chiqmasa:** `/media/` va `/static/` yo'llari (alias) Nginx konfiguratsiyasida to'g'ri ko'rsatilganiga ishonch hosil qiling.
