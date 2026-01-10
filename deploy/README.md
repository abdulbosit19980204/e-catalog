# E-Catalog Deployment Guide

Ushbu loyihani Production serverda (Linux/Ubuntu) ishga tushirish bo'yicha qo'llanma.

## 🏗️ Tizim arxitekturasi

- **Frontend Admin Panel:** `http://IP:1563/admin` (React orqali)
- **Backend (Django) Admin:** `http://IP:1563/backend-admin/` (Ma'lumotlar bazasi uchun)
- **API URL:** `http://IP:1563/api/v1/`
- **Server:** Nginx (Proxy sifatida 1563 portda)
- **Backend Process:** Gunicorn (unix socketda)

---

## 🔑 Admin Panellar farqi

Loyihada ikkita admin paneli mavjud:

1.  **Frontend Admin (`/admin`):** Bu loyihaning asosiy ishchi paneli bo'lib, unda Nomenklatura, Mijozlar va loyihalarni boshqarish qulay interfeysda amalga oshiriladi.
2.  **Django Admin (`/backend-admin/`):** Bu ma'lumotlar bazasini to'g'ridan-to'g'ri boshqarish (foydalanuvchilar qo'shish, texnik sozlamalar) uchun ishlatiladi. Konflikt bo'lmasligi uchun u `/backend-admin/`ga ko'chirildi.

---

## 🚀 O'rnatish qadamlari

### 1. Nginx Sozlamalari

Nginx konfiguratsiya fayllari `deploy/nginx/` papkasida joylashgan. Frontend Nginx fayli nafaqat statik fayllarni beradi, balki API so'rovlarni ham backend-ga (unix socket orqali) proxy qiladi.

```bash
# Backend uchun (ixtiyoriy, agar frontdan foydalanmasangiz)
sudo cp deploy/nginx/backend.conf /etc/nginx/sites-available/e-catalog-backend
sudo ln -s /etc/nginx/sites-available/e-catalog-backend /etc/nginx/sites-enabled/

# Frontend (va API Proxy) uchun - ASOSIY FAYL
sudo cp deploy/nginx/frontend.conf /etc/nginx/sites-available/e-catalog-frontend
sudo ln -s /etc/nginx/sites-available/e-catalog-frontend /etc/nginx/sites-enabled/

# Tekshirish va qayta yuklash
sudo nginx -t
sudo systemctl restart nginx
```

### 2. Frontend Build (MUHIM)

Production-da `npm start` ishlatilmaydi. Buning o'rniga statik fayllar (build) yaratiladi:

```bash
cd frontend
npm install
npm run build
```
*Eslatma: Nginx `frontend/build` papkasidagi tayyor fayllarni 1563-portda xizmat ko'rsatadi. `n.map is not a function` xatosi kelib chiqmasligi uchun `npm run build` qilinganiga ishonch hosil qiling.*

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
