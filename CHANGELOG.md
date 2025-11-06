# Changelog

E-Catalog Microservice o'zgarishlar tarixi.

## [1.0.0] - 2025-01-06

### Qo'shilgan
- Project modeli va API endpoint'lari
- Client modeli va API endpoint'lari
- Nomenklatura modeli va API endpoint'lari
- Image management - har bir entity uchun ko'p rasmlarni saqlash
- Rich text editor (CKEditor) - description maydonlari uchun
- RESTful API - to'liq CRUD operatsiyalari
- Soft delete - o'chirilgan ma'lumotlarni saqlash
- Filtering va Search - kengaytirilgan qidiruv va filtrlash
- Pagination - avtomatik sahifalash
- Image URL generation - to'liq URL'lar bilan rasm qaytarish
- Admin panel - barcha modellar uchun admin interfeysi
- Media file serving - development uchun media fayllarni serve qilish

### O'zgartirilgan
- Model munosabatlari - related_name qo'shildi
- Serializers - image_url maydoni qo'shildi
- Views - request context to'g'ri uzatiladi
- URL konfiguratsiyasi - media serve qo'shildi

### Tuzatilgan
- CKEditor URL - `ckeditr/` dan `ckeditor/` ga tuzatildi
- Static files warning - static papka yaratildi
- Nested serializers context - to'g'ri uzatiladi

### Dokumentatsiya
- README.md - asosiy loyiha haqida ma'lumot
- API_DOCUMENTATION.md - to'liq API qo'llanmasi
- SETUP.md - o'rnatish qo'llanmasi
- requirements.txt - kerakli paketlar ro'yxati
- .gitignore - Git ignore qoidalari

## [Unreleased]

## [1.1.0] - 2025-01-06

### Qo'shilgan
- **Authentication va Authorization** - JWT (JSON Web Token) authentication qo'shildi
  - Token olish: `/api/token/`
  - Token yangilash: `/api/token/refresh/`
  - Token tekshirish: `/api/token/verify/`
- **API Rate Limiting** - So'rovlar sonini cheklash
  - Anonim foydalanuvchilar: 100 so'rov/soat
  - Autentifikatsiya qilingan foydalanuvchilar: 1000 so'rov/soat
- **CORS Sozlamalari** - Frontend bilan integratsiya uchun CORS qo'llab-quvvatlash
- **Unit Testlar** - API endpoint'lar uchun testlar
- **Docker Containerization** - Dockerfile va docker-compose.yml
- **CI/CD Pipeline** - GitHub Actions orqali avtomatik test va build
- **Production Sozlamalari** - Production uchun optimallashtirilgan sozlamalar
- **Deployment Qo'llanmasi** - Serverda ishga tushirish bo'yicha batafsil qo'llanma

### O'zgartirilgan
- API endpoint'lar authentication talab qiladi (read-only operatsiyalar ochiq)
- Settings.py environment variables bilan ishlaydi
- Requirements.txt yangi paketlar qo'shildi

### Xavfsizlik
- JWT authentication
- Rate limiting
- CORS sozlamalari
- Production uchun xavfsizlik sozlamalari

