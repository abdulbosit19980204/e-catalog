# E-Catalog Microservice

E-Catalog Microservice - Project, Nomenklatura va Client ma'lumotlarini boshqarish uchun Django REST Framework asosida yaratilgan microservice.

## 🚀 Features

- **Project Management** - Project'lar va ularning rasmlarini boshqarish
- **Nomenklatura Management** - Nomenklatura'lar va ularning rasmlarini boshqarish
- **Client Management** - Client'lar va ularning rasmlarini boshqarish
- **1C Integration** - 1C dan ma'lumotlarni yuklab olish (background tasks bilan)
- **JWT Authentication** - Token-based authentication
- **API Documentation** - Swagger UI va ReDoc
- **CORS Support** - Frontend integratsiya uchun
- **Excel Import/Export** - Ma'lumotlarni Excel formatida import/export qilish
- **AI Description Generator** - OpenAI yordamida professional descriptionlar yaratish
- **High Performance** - Redis caching va background tasks (10K+ requests/minute)
- **Image Management** - Ko'p o'lchamdagi rasmlar, status va source tracking
- **Agent Location Tracking** - Mobil agentlar uchun geolokatsiya va qurilma ma'lumotlari
- **Docker Support** - Docker containerization
- **Production Ready** - Production uchun tayyor

## 📋 Requirements

- Python 3.11+
- Django 5.2.7
- PostgreSQL (production uchun)
- SQLite (development uchun)

## 🔧 Installation

### 1. Virtual Environment yaratish

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# yoki
venv\Scripts\activate  # Windows
```

### 2. Paketlarni o'rnatish

```bash
pip install -r requirements.txt
```

### 3. Environment Variables

`.env` faylini yaratish:

```env
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
DATABASE_URL=sqlite:///db.sqlite3
CORS_ALLOWED_ORIGINS=http://localhost:3000
```

### 4. Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### 5. Superuser yaratish

```bash
python manage.py createsuperuser
```

### 6. Server ishga tushirish

```bash
python manage.py runserver
```

## 📚 API Documentation

- **Swagger UI**: http://localhost:8000/api/docs/
- **ReDoc**: http://localhost:8000/api/redoc/
- **OpenAPI Schema**: http://localhost:8000/api/schema/

## 🔗 API Endpoints

### Authentication
- `POST /api/token/` - Token olish
- `POST /api/token/refresh/` - Token yangilash
- `POST /api/token/verify/` - Token tekshirish

### Project API
- `GET /api/v1/project/` - Project ro'yxati
- `POST /api/v1/project/` - Yangi project yaratish
- `GET /api/v1/project/{code_1c}/` - Bitta project
- `PUT /api/v1/project/{code_1c}/` - Project yangilash
- `DELETE /api/v1/project/{code_1c}/` - Project o'chirish

### Client API
- `GET /api/v1/client/` - Client ro'yxati
- `POST /api/v1/client/` - Yangi client yaratish
- `GET /api/v1/client/{client_code_1c}/` - Bitta client
- `PUT /api/v1/client/{client_code_1c}/` - Client yangilash
- `DELETE /api/v1/client/{client_code_1c}/` - Client o'chirish

### Nomenklatura API
- `GET /api/v1/nomenklatura/` - Nomenklatura ro'yxati
- `POST /api/v1/nomenklatura/` - Yangi nomenklatura yaratish
- `GET /api/v1/nomenklatura/{code_1c}/` - Bitta nomenklatura
- `PUT /api/v1/nomenklatura/{code_1c}/` - Nomenklatura yangilash
- `DELETE /api/v1/nomenklatura/{code_1c}/` - Nomenklatura o'chirish

### Integration API
- `POST /api/v1/integration/sync/nomenklatura/{integration_id}/` - 1C dan nomenklatura yuklab olish (background task)
- `POST /api/v1/integration/sync/clients/{integration_id}/` - 1C dan client yuklab olish (background task)
- `GET /api/v1/integration/sync/status/{task_id}/` - Sync progress

### Excel Import/Export API
- `GET /api/v1/project/export-xlsx/` - Project ma'lumotlarini Excel formatida eksport qilish
- `GET /api/v1/project/template-xlsx/` - Project Excel shablonini yuklab olish
- `POST /api/v1/project/import-xlsx/` - Project ma'lumotlarini Excel fayldan import qilish
- `GET /api/v1/client/export-xlsx/` - Client ma'lumotlarini Excel formatida eksport qilish
- `GET /api/v1/client/template-xlsx/` - Client Excel shablonini yuklab olish
- `POST /api/v1/client/import-xlsx/` - Client ma'lumotlarini Excel fayldan import qilish
- `GET /api/v1/nomenklatura/export-xlsx/` - Nomenklatura ma'lumotlarini Excel formatida eksport qilish
- `GET /api/v1/nomenklatura/template-xlsx/` - Nomenklatura Excel shablonini yuklab olish
- `POST /api/v1/nomenklatura/import-xlsx/` - Nomenklatura ma'lumotlarini Excel fayldan import qilish

### Thumbnail API
- `GET /api/v1/thumbnails/` - Barcha entity'lar uchun thumbnail rasmlar
- `GET /api/v1/thumbnails/projects/` - Faqat Project thumbnail rasmlari
- `GET /api/v1/thumbnails/clients/` - Faqat Client thumbnail rasmlari
- `GET /api/v1/thumbnails/nomenklatura/` - Faqat Nomenklatura thumbnail rasmlari

### Agent Location API
- `GET /api/v1/agent-location/` - Agent lokatsiya yozuvlari ro'yxati
- `POST /api/v1/agent-location/` - Yangi agent lokatsiyasi yaratish

## 🐳 Docker

### Docker Compose orqali

```bash
docker-compose up -d
```

### Docker Image Build

```bash
docker build -t ecatalog:latest .
```

## 📖 Documentation

- [API Documentation](API_DOCUMENTATION.md)
- [Integration API](INTEGRATION_API.md)
- [Integration Admin Guide](INTEGRATION_ADMIN_GUIDE.md)
- [Deployment Guide](DEPLOYMENT.md)
- [Setup Guide](SETUP.md)
- [Integration Guide](INTEGRATION_GUIDE.md)
- [Production Checklist](PRODUCTION_CHECKLIST.md)
- [AI Description Generator](scripts/README_DESCRIPTIONS.md)

## 🤖 AI Description Generator

Nomenklatura va Client modellariga AI yordamida professional descriptionlar yozish:

```bash
# Test qilish (dry-run)
python manage.py generate_descriptions --nomenklatura --dry-run --limit 5

# Haqiqiy ishlatish
python manage.py generate_descriptions --nomenklatura
python manage.py generate_descriptions --client
```

Batafsil ma'lumot: [scripts/README_DESCRIPTIONS.md](scripts/README_DESCRIPTIONS.md)

## ⚡ Performance Optimizations

- **Redis Caching** - API viewlar va ORM querylar uchun caching
- **Background Tasks** - 1C sync operatsiyalari background'da ishlaydi
- **SQLite WAL Mode** - Concurrent write operatsiyalar uchun optimizatsiya
- **Bulk Operations** - Ko'p yozuvlarni bir vaqtda qayta ishlash
- **Chunking** - Excel export uchun chunking (SQLite limit muammosini hal qiladi)

## 🧪 Testing

```bash
python manage.py test
```

## 📝 License

MIT License

## 👥 Contributors

- Development Team

## 🔄 Changelog

[CHANGELOG.md](CHANGELOG.md) faylida batafsil o'zgarishlar ro'yxati.
