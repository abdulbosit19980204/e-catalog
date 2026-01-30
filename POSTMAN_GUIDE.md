# Postman Collection - Foydalanish Qo'llanmasi

## Fayllar
1. **E-Catalog_API_Collection.postman_collection.json** - Barcha API endpoint'lar
2. **E-Catalog_Environment.postman_environment.json** - Environment o'zgaruvchilari

## Import Qilish

### 1. Collection'ni Import Qilish
1. Postman'ni oching
2. **Import** tugmasini bosing
3. `E-Catalog_API_Collection.postman_collection.json` faylini tanlang
4. **Import** tugmasini bosing

### 2. Environment'ni Import Qilish
1. Postman'da **Environments** bo'limiga o'ting
2. **Import** tugmasini bosing
3. `E-Catalog_Environment.postman_environment.json` faylini tanlang
4. **Import** tugmasini bosing
5. O'ng yuqori burchakda "E-Catalog Environment"ni tanlang

## Foydalanish

### Birinchi Qadam: Authentication
1. **Authentication** → **Obtain Token** request'ini oching
2. Body'da `username` va `password`ni kiriting
3. **Send** tugmasini bosing
4. Token avtomatik ravishda `access_token` va `refresh_token` o'zgaruvchilariga saqlanadi

### API'larni Sinash

#### License Management
- **Check License Status**: Mobile app litsenziyasini tekshirish
- **Get Access History**: Kirish tarixini ko'rish
- **Filter History**: Ma'lum litsenziya bo'yicha filtrlash

#### Client API
- **List Clients**: Barcha mijozlarni ko'rish
- **Get Client Details**: Bitta mijoz ma'lumotlarini olish

#### Nomenklatura API
- **List Products**: Mahsulotlar ro'yxati
- **Enrich Product**: AI yordamida mahsulotni boyitish

#### Visit Management
- **List Visits**: Tashriflar ro'yxati
- **Create Visit**: Yangi tashrif yaratish

#### Core & Health
- **Health Check**: Tizim holatini tekshirish
- **AI Usage Stats**: AI foydalanish statistikasi

## Environment O'zgaruvchilari

- `base_url`: Server manzili (default: http://localhost:8000)
- `access_token`: JWT access token (avtomatik to'ldiriladi)
- `refresh_token`: JWT refresh token (avtomatik to'ldiriladi)
- `license_key`: Test litsenziya kaliti
- `project_code`: Proyekt kodi

## Muhim Eslatmalar

1. **Authentication**: Dastlab "Obtain Token" request'ini yuboring
2. **Auto Token**: Token avtomatik saqlanadi va barcha request'larda ishlatiladi
3. **Environment**: Har doim to'g'ri environment tanlangan bo'lsin
4. **Base URL**: Production uchun `base_url`ni o'zgartiring

## Production Sozlamalari

Production muhitida foydalanish uchun:
1. Environment'ni duplicate qiling
2. `base_url`ni production serverga o'zgartiring:
   ```
   https://your-production-server.com
   ```
3. Yangi environment'ni "Production" deb nomlang
