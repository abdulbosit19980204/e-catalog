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

## [1.3.0] - 2025-11-26

### Qo'shilgan
- **Client Model Kengaytirildi** - Client modeliga keng qamrovli maydonlar qo'shildi
  - Kompaniya ma'lumotlari: `company_name`, `tax_id`, `registration_number`, `legal_address`, `actual_address`
  - Aloqa ma'lumotlari: `fax`, `website`, `social_media` (JSON), `additional_phones` (JSON)
  - Biznes ma'lumotlari: `industry`, `business_type`, `employee_count`, `annual_revenue`, `established_date`
  - Moliyaviy ma'lumotlar: `payment_terms`, `credit_limit`, `currency`
  - Lokatsiya: `city`, `region`, `country`, `postal_code`
  - Kontakt shaxs: `contact_person`, `contact_position`, `contact_email`, `contact_phone`
  - Qo'shimcha: `notes`, `tags` (JSON), `rating`, `priority`, `source`, `metadata` (JSON)
- **Nomenklatura Model Kengaytirildi** - Nomenklatura modeliga keng qamrovli maydonlar qo'shildi
  - Mahsulot identifikatsiyasi: `sku`, `barcode`, `brand`, `manufacturer`, `model`, `series`, `vendor_code`
  - Narx ma'lumotlari: `base_price`, `sale_price`, `cost_price`, `currency`, `discount_percent`, `tax_rate`
  - Ombor ma'lumotlari: `stock_quantity`, `min_stock`, `max_stock`, `unit_of_measure`, `weight`, `dimensions`, `volume`
  - Kategoriya: `category`, `subcategory`, `tags` (JSON)
  - Texnik xususiyatlar: `color`, `size`, `material`, `warranty_period`, `expiry_date`, `production_date`
  - Qo'shimcha: `notes`, `rating`, `popularity_score`, `seo_keywords`, `source`, `metadata` (JSON)
- **Database Indexes** - Qidiruv va filtrlash uchun yangi indexlar qo'shildi
  - Client: `city`, `region`, `industry`, `business_type`, `rating`, `priority`
  - Nomenklatura: `sku`, `barcode`, `category`, `subcategory`, `brand`, `manufacturer`, `rating`, `popularity_score`
- **Excel Export/Import Yangilandi** - Barcha yangi maydonlar Excel export/import qo'llab-quvvatlanadi
  - Client: 33 ta maydon export/import qilinadi
  - Nomenklatura: 38 ta maydon export/import qilinadi

### O'zgartirilgan
- **Admin Panellar** - Barcha yangi maydonlar fieldsets ga qo'shildi va tuzatildi
  - Client admin: 10 ta fieldsets (Asosiy, Kompaniya, Aloqa, Biznes, Moliyaviy, Lokatsiya, Kontakt shaxs, Qo'shimcha, Status, Statistika, Vaqt)
  - Nomenklatura admin: 9 ta fieldsets (Asosiy, Mahsulot identifikatsiyasi, Narx, Ombor, Kategoriya, Texnik xususiyatlar, Qo'shimcha, Status, Statistika, Vaqt)
- **Search Fields** - Qidiruv maydonlari kengaytirildi
  - Client: `company_name`, `tax_id`, `contact_person`, `city`, `region` qo'shildi
  - Nomenklatura: `sku`, `barcode`, `brand`, `manufacturer`, `model`, `category` qo'shildi
- **API Dokumentatsiya** - Barcha yangi maydonlar API dokumentatsiyasiga qo'shildi
  - Response misollari yangilandi
  - Request Body misollari yangilandi
  - Optional fields ro'yxati to'liq qo'shildi

### Tuzatilgan
- Barcha yangi maydonlar ixtiyoriy (`blank=True, null=True`) - mavjud ma'lumotlar saqlanadi
- Serializers avtomatik yangi maydonlarni qo'llab-quvvatlaydi (`fields = '__all__'`)

## [1.2.0] - 2025-11-26

### Qo'shilgan
- **Excel Import/Export** - Project, Client va Nomenklatura uchun Excel import/export funksiyalari
  - Export: `/api/v1/{entity}/export-xlsx/` - Ma'lumotlarni Excel formatida eksport qilish
  - Template: `/api/v1/{entity}/template-xlsx/` - Excel shablonini yuklab olish
  - Import: `/api/v1/{entity}/import-xlsx/` - Excel fayldan ma'lumotlarni import qilish
  - Chunking optimizatsiyasi - SQLite "too many SQL variables" muammosini hal qiladi
- **AI Description Generator** - OpenAI yordamida professional descriptionlar yaratish
  - Django management command: `python manage.py generate_descriptions`
  - Nomenklatura va Client uchun AI yordamida description yozish
  - Dry-run rejimi test uchun
- **Image Status va Source Tracking** - Rasmlar uchun status va source tracking
  - `ImageStatus` modeli - Rasm holatini belgilash
  - `ImageSource` modeli - Rasm manbasini kuzatish
  - Image modellariga `status` va `source` maydonlari qo'shildi
- **Thumbnail API** - Thumbnail rasmlarni olish uchun alohida endpoint'lar
  - `/api/v1/thumbnails/` - Barcha entity'lar uchun
  - `/api/v1/thumbnails/projects/` - Faqat Project uchun
  - `/api/v1/thumbnails/clients/` - Faqat Client uchun
  - `/api/v1/thumbnails/nomenklatura/` - Faqat Nomenklatura uchun
- **Agent Location Tracking** - Mobil agentlar uchun kengaytirilgan geolokatsiya va qurilma ma'lumotlari
  - Device info (manufacturer, model, OS, screen, RAM, storage, camera)
  - Location data (city, country, timezone, location provider)
  - Network info (WiFi, cellular, IP address)
  - Sensor data (accelerometer, gyroscope, magnetometer, proximity, light)
  - Battery info (level, health, temperature, voltage)
  - Security info (fingerprint, rooted/jailbroken, encryption, screen lock)
- **Date-based Filtering** - Barcha API'lar uchun sana bo'yicha filtrlash
  - `created_from`, `created_to` - Yaratilgan sana bo'yicha
  - `updated_from`, `updated_to` - Yangilangan sana bo'yicha
- **Description Status Filtering** - Description bor/yo'q bo'yicha filtrlash
  - `description_status=with` - Description bor
  - `description_status=without` - Description yo'q
- **Image Category va Note** - Rasmlar uchun toifa va izoh maydonlari
  - `category` - Rasm toifasi yoki teg
  - `note` - Rasm haqida qo'shimcha izoh
- **Django Admin Redesign** - Zamonaviy va chiroyli admin interfeysi
  - Asosiy dashboard redesign
  - Import/Export dashboard
  - Sidebar menu redesign
- **High Performance Optimizations** - 10K+ requests/minute uchun optimizatsiya
  - Redis caching - API viewlar va ORM querylar uchun
  - Background tasks - 1C sync operatsiyalari background'da
  - SQLite WAL mode - Concurrent write operatsiyalar uchun
  - Bulk operations - Ko'p yozuvlarni bir vaqtda qayta ishlash
  - Connection pooling - Database connection'lar pool'da

### O'zgartirilgan
- **Export-XLSX Optimizatsiyasi** - Chunking va iterator() ishlatiladi
  - SQLite "too many SQL variables" muammosini hal qiladi
  - Memory-efficient processing
  - 1000 ta yozuv chunk'larida qayta ishlash
- **1C Integration** - Background tasks bilan ishlaydi
  - `django-q2` o'rniga threading ishlatiladi (Django 5.2 bilan mos keladi)
  - Bulk operations bilan optimizatsiya
  - Retry mechanism qo'shildi
- **Filtering** - Kengaytirilgan filtrlash imkoniyatlari
  - Date-based filtering barcha API'lar uchun
  - Description status filtering
- **Image Models** - `category` va `note` maydonlari qo'shildi
- **Admin Interface** - Zamonaviy dizayn va yaxshilangan UX

### Tuzatilgan
- **SQLite Concurrency** - "database is locked" va "readonly database" xatoliklari
  - WAL mode yoqildi
  - Connection timeout oshirildi
  - `check_same_thread=False` qo'shildi
- **Export-XLSX SQLite Limit** - "too many SQL variables" xatoligi
  - Chunking implementatsiyasi
  - Iterator() metodidan foydalanish
  - `prefetch_related` export uchun olib tashlandi
- **URL Namespace** - API URL namespace muammosi tuzatildi
- **Image Serializers** - `get_image_url` metodlari qo'shildi

### Dokumentatsiya
- [AI Description Generator Guide](scripts/README_DESCRIPTIONS.md) - AI description generator qo'llanmasi
- API_DOCUMENTATION.md - Excel import/export, Thumbnail API, Agent Location API qo'shildi
- README.md - Yangi xususiyatlar va performance optimizations qo'shildi

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

