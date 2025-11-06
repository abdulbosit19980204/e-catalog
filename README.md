# E-Catalog Microservice

E-Catalog Microservice - Project, Nomenklatura va Client ma'lumotlarini boshqarish uchun Django REST Framework asosida yaratilgan microservice.

## 🚀 Features

- **Project Management** - Project'lar va ularning rasmlarini boshqarish
- **Nomenklatura Management** - Nomenklatura'lar va ularning rasmlarini boshqarish
- **Client Management** - Client'lar va ularning rasmlarini boshqarish
- **1C Integration** - 1C dan ma'lumotlarni yuklab olish
- **JWT Authentication** - Token-based authentication
- **API Documentation** - Swagger UI va ReDoc
- **CORS Support** - Frontend integratsiya uchun
- **Rate Limiting** - API rate limiting
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
- `POST /api/v1/integration/sync/nomenklatura/{integration_id}/` - 1C dan nomenklatura yuklab olish
- `POST /api/v1/integration/sync/clients/{integration_id}/` - 1C dan client yuklab olish
- `GET /api/v1/integration/sync/status/{task_id}/` - Sync progress

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
