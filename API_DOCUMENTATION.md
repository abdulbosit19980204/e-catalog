# API Dokumentatsiyasi

E-Catalog Microservice API to'liq qo'llanmasi.

## Base URL

```
http://localhost:8000/api/v1/
```

## Umumiy API Xususiyatlari

- **Content-Type**: `application/json`
- **Pagination**: 20 ta element per page
- **Search**: `?search=query` parametri orqali (barcha search_fields maydonlarida qidirish)
- **Filtering**: `?field_name=value` parametri orqali maydon bo'yicha filtrlash
- **Ordering**: `?ordering=field_name` yoki `?ordering=-field_name` (teskari tartib)
- **Soft Delete**: O'chirilgan ma'lumotlar avtomatik filtrlashadi

### Search va Filtering

**Search** - `?search=query` parametri orqali barcha `search_fields` maydonlarida qidirish:
- Project: `code_1c`, `name`, `title` maydonlarida qidirish
- Client: `client_code_1c`, `name`, `email` maydonlarida qidirish
- Nomenklatura: `code_1c`, `name` maydonlarida qidirish

**Filtering** - `?field_name=value` parametri orqali aniq maydon bo'yicha filtrlash:
- Project: `?code_1c=PROJ001&name=Test`
- Client: `?client_code_1c=CLI001&name=Test&email=test@example.com`
- Nomenklatura: `?code_1c=NOM001&name=Test`

**Ordering** - `?ordering=field_name` parametri orqali tartiblash:
- `?ordering=name` - nom bo'yicha o'sish tartibida
- `?ordering=-created_at` - yaratilgan sana bo'yicha kamayish tartibida
- `?ordering=name,-created_at` - bir nechta maydon bo'yicha tartiblash

### Misollar

```bash
# Search - barcha maydonlarda qidirish
GET /api/v1/project/?search=test

# Filtering - aniq maydon bo'yicha filtrlash
GET /api/v1/project/?code_1c=PROJ001&name=Test

# Ordering - tartiblash
GET /api/v1/project/?ordering=-created_at

# Kombinatsiya
GET /api/v1/project/?search=test&code_1c=PROJ001&ordering=-created_at
```

## Response Format

Barcha muvaffaqiyatli so'rovlar `200 OK` status code bilan qaytadi.

### Muvaffaqiyatli Response
```json
{
  "id": 1,
  "code_1c": "PROJ001",
  "name": "Loyiha Nomi",
  "description": "<p>Description</p>",
  "images": [
    {
      "id": 1,
      "image": "/media/projects/image.jpg",
      "image_url": "http://localhost:8000/media/projects/image.jpg",
      "is_main": true
    }
  ],
  "is_active": true,
  "created_at": "2025-01-01T00:00:00Z",
  "updated_at": "2025-01-01T00:00:00Z"
}
```

### Xato Response
```json
{
  "detail": "Xato xabari",
  "field_name": ["Xato tafsilotlari"]
}
```

---

## Project API

### 1. Barcha Project'larni olish

**GET** `/api/v1/project/`

**Query Parameters:**

**Search:**
- `search` - `code_1c`, `name`, `title` maydonlarida qidirish
  - Misol: `?search=test` - "test" so'zini barcha maydonlarda qidiradi

**Filtering:**
- `code_1c` - Kod bo'yicha filtrlash (to'liq mos kelishi kerak)
  - Misol: `?code_1c=PROJ001`
- `name` - Nom bo'yicha filtrlash (to'liq mos kelishi kerak)
  - Misol: `?name=Test Project`

**Ordering:**
- `ordering` - Tartiblash (maydon nomi yoki `-maydon_nomi` teskari tartib uchun)
  - Misol: `?ordering=-created_at` - Eng yangi avval
  - Misol: `?ordering=name` - Nom bo'yicha alfavit tartibida

**Pagination:**
- `page` - Sahifa raqami
  - Misol: `?page=2`

**Response:**
```json
{
  "count": 10,
  "next": "http://localhost:8000/api/v1/project/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "code_1c": "PROJ001",
      "name": "Loyiha Nomi",
      "title": "Sarlavha",
      "description": "<p>Description</p>",
      "images": [],
      "is_active": true,
      "is_deleted": false,
      "created_at": "2025-01-01T00:00:00Z",
      "updated_at": "2025-01-01T00:00:00Z"
    }
  ]
}
```

### 2. Bitta Project olish

**GET** `/api/v1/project/{code_1c}/`

**Response:**
```json
{
  "id": 1,
  "code_1c": "PROJ001",
  "name": "Loyiha Nomi",
  "title": "Sarlavha",
  "description": "<p>Description</p>",
  "images": [
    {
      "id": 1,
      "image": "/media/projects/image.jpg",
      "image_url": "http://localhost:8000/media/projects/image.jpg",
      "is_main": true,
      "created_at": "2025-01-01T00:00:00Z"
    }
  ],
  "is_active": true,
  "is_deleted": false,
  "created_at": "2025-01-01T00:00:00Z",
  "updated_at": "2025-01-01T00:00:00Z"
}
```

### 3. Yangi Project yaratish

**POST** `/api/v1/project/`

**Request Body:**
```json
{
  "code_1c": "PROJ001",
  "name": "Yangi Loyiha",
  "title": "Loyiha Sarlavhasi",
  "description": "<p>Loyiha haqida ma'lumot</p>",
  "is_active": true
}
```

**Required Fields:**
- `code_1c` - 1C kodi (unique)
- `name` - Nomi

**Optional Fields:**
- `title` - Sarlavha
- `description` - Tavsif (HTML formatida)
- `is_active` - Faollik holati (default: true)

### 4. Project yangilash

**PUT** `/api/v1/project/{code_1c}/` - To'liq yangilash
**PATCH** `/api/v1/project/{code_1c}/` - Qisman yangilash

**Request Body:**
```json
{
  "name": "Yangilangan Nom",
  "description": "<p>Yangilangan description</p>"
}
```

### 5. Project o'chirish

**DELETE** `/api/v1/project/{code_1c}/`

**Response:** `204 No Content`

---

## Project Image API

### 1. Barcha Project rasmlarini olish

**GET** `/api/v1/project-image/`

**Query Parameters:**

**Filtering:**
- `project` - Project ID bo'yicha filtrlash
  - Misol: `?project=1`
- `is_main` - Asosiy rasm bo'yicha filtrlash (true/false)
  - Misol: `?is_main=true`

**Search:**
- `search` - Project `code_1c` va `name` maydonlarida qidirish
  - Misol: `?search=test`

**Ordering:**
- `ordering` - Tartiblash
  - Misol: `?ordering=-created_at`

**Pagination:**
- `page` - Sahifa raqami

### 2. Bitta Project rasm olish

**GET** `/api/v1/project-image/{id}/`

### 3. Yangi Project rasm yuklash

**POST** `/api/v1/project-image/`

**Request Body (multipart/form-data):**
```
project: 1
image: [file]
is_main: true
```

**cURL Misol:**
```bash
curl -X POST http://localhost:8000/api/v1/project-image/ \
  -F "project=1" \
  -F "image=@/path/to/image.jpg" \
  -F "is_main=true"
```

### 4. Project rasm yangilash

**PUT** `/api/v1/project-image/{id}/`
**PATCH** `/api/v1/project-image/{id}/`

### 5. Project rasm o'chirish

**DELETE** `/api/v1/project-image/{id}/`

---

## Client API

### 1. Barcha Client'larni olish

**GET** `/api/v1/client/`

**Query Parameters:**

**Search:**
- `search` - `client_code_1c`, `name`, `email` maydonlarida qidirish
  - Misol: `?search=test`

**Filtering:**
- `client_code_1c` - Kod bo'yicha filtrlash
  - Misol: `?client_code_1c=CLI001`
- `name` - Nom bo'yicha filtrlash
  - Misol: `?name=Test Client`
- `email` - Email bo'yicha filtrlash
  - Misol: `?email=test@example.com`

**Ordering:**
- `ordering` - Tartiblash
  - Misol: `?ordering=-created_at`

**Pagination:**
- `page` - Sahifa raqami

### 2. Bitta Client olish

**GET** `/api/v1/client/{client_code_1c}/`

**Response:**
```json
{
  "id": 1,
  "client_code_1c": "CLI001",
  "name": "Mijoz Nomi",
  "email": "client@example.com",
  "phone": "+998901234567",
  "description": "<p>Mijoz haqida ma'lumot</p>",
  "images": [],
  "is_active": true,
  "is_deleted": false,
  "created_at": "2025-01-01T00:00:00Z",
  "updated_at": "2025-01-01T00:00:00Z"
}
```

### 3. Yangi Client yaratish

**POST** `/api/v1/client/`

**Request Body:**
```json
{
  "client_code_1c": "CLI001",
  "name": "Yangi Mijoz",
  "email": "newclient@example.com",
  "phone": "+998901234567",
  "description": "<p>Mijoz haqida ma'lumot</p>",
  "is_active": true
}
```

**Required Fields:**
- `client_code_1c` - 1C kodi
- `name` - Nomi

**Optional Fields:**
- `email` - Email
- `phone` - Telefon
- `description` - Tavsif (HTML formatida)
- `is_active` - Faollik holati (default: true)

### 4. Client yangilash

**PUT** `/api/v1/client/{client_code_1c}/`
**PATCH** `/api/v1/client/{client_code_1c}/`

### 5. Client o'chirish

**DELETE** `/api/v1/client/{client_code_1c}/`

---

## Client Image API

### 1. Barcha Client rasmlarini olish

**GET** `/api/v1/client-image/`

**Query Parameters:**

**Filtering:**
- `client` - Client ID bo'yicha filtrlash
  - Misol: `?client=1`
- `is_main` - Asosiy rasm bo'yicha filtrlash (true/false)
  - Misol: `?is_main=true`

**Search:**
- `search` - Client `client_code_1c` va `name` maydonlarida qidirish
  - Misol: `?search=test`

**Ordering:**
- `ordering` - Tartiblash
  - Misol: `?ordering=-created_at`

**Pagination:**
- `page` - Sahifa raqami

### 2. Yangi Client rasm yuklash

**POST** `/api/v1/client-image/`

**Request Body (multipart/form-data):**
```
client: 1
image: [file]
is_main: true
```

---

## Nomenklatura API

### 1. Barcha Nomenklatura'larni olish

**GET** `/api/v1/nomenklatura/`

**Query Parameters:**

**Search:**
- `search` - `code_1c`, `name` maydonlarida qidirish
  - Misol: `?search=test`

**Filtering:**
- `code_1c` - Kod bo'yicha filtrlash
  - Misol: `?code_1c=NOM001`
- `name` - Nom bo'yicha filtrlash
  - Misol: `?name=Test Nomenklatura`

**Ordering:**
- `ordering` - Tartiblash
  - Misol: `?ordering=-created_at`

**Pagination:**
- `page` - Sahifa raqami

### 2. Bitta Nomenklatura olish

**GET** `/api/v1/nomenklatura/{code_1c}/`

**Response:**
```json
{
  "id": 1,
  "code_1c": "NOM001",
  "name": "Nomenklatura Nomi",
  "title": "Sarlavha",
  "description": "<p>Nomenklatura haqida ma'lumot</p>",
  "images": [],
  "is_active": true,
  "is_deleted": false,
  "created_at": "2025-01-01T00:00:00Z",
  "updated_at": "2025-01-01T00:00:00Z"
}
```

### 3. Yangi Nomenklatura yaratish

**POST** `/api/v1/nomenklatura/`

**Request Body:**
```json
{
  "code_1c": "NOM001",
  "name": "Yangi Nomenklatura",
  "title": "Sarlavha",
  "description": "<p>Nomenklatura haqida ma'lumot</p>",
  "is_active": true
}
```

**Required Fields:**
- `code_1c` - 1C kodi
- `name` - Nomi

**Optional Fields:**
- `title` - Sarlavha
- `description` - Tavsif (HTML formatida)
- `is_active` - Faollik holati (default: true)

### 4. Nomenklatura yangilash

**PUT** `/api/v1/nomenklatura/{code_1c}/`
**PATCH** `/api/v1/nomenklatura/{code_1c}/`

### 5. Nomenklatura o'chirish

**DELETE** `/api/v1/nomenklatura/{code_1c}/`

---

## Nomenklatura Image API

### 1. Barcha Nomenklatura rasmlarini olish

**GET** `/api/v1/nomenklatura-image/`

**Query Parameters:**

**Filtering:**
- `nomenklatura` - Nomenklatura ID bo'yicha filtrlash
  - Misol: `?nomenklatura=1`
- `is_main` - Asosiy rasm bo'yicha filtrlash (true/false)
  - Misol: `?is_main=true`

**Search:**
- `search` - Nomenklatura `code_1c` va `name` maydonlarida qidirish
  - Misol: `?search=test`

**Ordering:**
- `ordering` - Tartiblash
  - Misol: `?ordering=-created_at`

**Pagination:**
- `page` - Sahifa raqami

### 2. Yangi Nomenklatura rasm yuklash

**POST** `/api/v1/nomenklatura-image/`

**Request Body (multipart/form-data):**
```
nomenklatura: 1
image: [file]
is_main: true
```

---

## Excel Import/Export API

### Project Excel Export/Import

#### 1. Project ma'lumotlarini Excel formatida eksport qilish

**GET** `/api/v1/project/export-xlsx/`

**Query Parameters:**
- Barcha filter parametrlari qo'llaniladi (search, code_1c, name, description_status, created_from, created_to, updated_from, updated_to)

**Response:**
- Content-Type: `application/vnd.openxmlformats-officedocument.spreadsheetml.sheet`
- XLSX fayl yuklab olinadi

**Eslatma:** 
- Ko'p yozuvlar bilan ishlash uchun chunking ishlatiladi (har safar 1000 ta yozuv)
- SQLite "too many SQL variables" muammosini hal qiladi
- Memory-efficient iterator() metodidan foydalanadi

**Misol:**
```bash
curl -X GET "http://localhost:8000/api/v1/project/export-xlsx/?search=test" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -o projects.xlsx
```

#### 2. Project Excel shablonini yuklab olish

**GET** `/api/v1/project/template-xlsx/`

**Response:**
- XLSX shablon fayl yuklab olinadi
- Namuna ma'lumotlar bilan to'ldirilgan

#### 3. Project ma'lumotlarini Excel fayldan import qilish

**POST** `/api/v1/project/import-xlsx/`

**Request Body (multipart/form-data):**
```
file: [XLSX file]
```

**Response:**
```json
{
  "created": 10,
  "updated": 5,
  "errors": []
}
```

**Excel Format:**
- Headers: `code_1c`, `name`, `title`, `description`, `is_active`
- Birinchi qator headerlar, keyingi qatorlar ma'lumotlar

### Client Excel Export/Import

#### 1. Client ma'lumotlarini Excel formatida eksport qilish

**GET** `/api/v1/client/export-xlsx/`

**Query Parameters:**
- Barcha filter parametrlari qo'llaniladi

**Misol:**
```bash
curl -X GET "http://localhost:8000/api/v1/client/export-xlsx/?description_status=without" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -o clients.xlsx
```

#### 2. Client Excel shablonini yuklab olish

**GET** `/api/v1/client/template-xlsx/`

#### 3. Client ma'lumotlarini Excel fayldan import qilish

**POST** `/api/v1/client/import-xlsx/`

**Excel Format:**
- Headers: `client_code_1c`, `name`, `email`, `phone`, `description`, `is_active`

### Nomenklatura Excel Export/Import

#### 1. Nomenklatura ma'lumotlarini Excel formatida eksport qilish

**GET** `/api/v1/nomenklatura/export-xlsx/`

**Query Parameters:**
- Barcha filter parametrlari qo'llaniladi

#### 2. Nomenklatura Excel shablonini yuklab olish

**GET** `/api/v1/nomenklatura/template-xlsx/`

#### 3. Nomenklatura ma'lumotlarini Excel fayldan import qilish

**POST** `/api/v1/nomenklatura/import-xlsx/`

**Excel Format:**
- Headers: `code_1c`, `name`, `title`, `description`, `is_active`

---

## Thumbnail API

### 1. Barcha entity'lar uchun thumbnail rasmlar

**GET** `/api/v1/thumbnails/`

**Query Parameters:**
- `entity_type` - Entity turi (`project`, `client`, `nomenklatura`)
- `is_main` - Asosiy rasm bo'yicha filter (true/false)
- `status` - Rasm statusi bo'yicha filter

**Response:**
```json
{
  "count": 100,
  "results": [
    {
      "entity_type": "project",
      "entity_code_1c": "PROJ001",
      "entity_name": "Project Name",
      "thumbnail_url": "http://localhost:8000/media/projects/thumb.jpg",
      "is_main": true
    }
  ]
}
```

### 2. Project thumbnail rasmlari

**GET** `/api/v1/thumbnails/projects/`

### 3. Client thumbnail rasmlari

**GET** `/api/v1/thumbnails/clients/`

### 4. Nomenklatura thumbnail rasmlari

**GET** `/api/v1/thumbnails/nomenklatura/`

---

## Agent Location API

### 1. Agent lokatsiya yozuvlari ro'yxati

**GET** `/api/v1/agent-location/`

**Query Parameters:**
- `agent_code` - Agent kodi bo'yicha filter
- `region` - Hudud bo'yicha filter
- `platform` - Platforma bo'yicha filter (Android/iOS)
- `device_id` - Qurilma ID bo'yicha filter
- `date_from` - Yaratilgan vaqtdan boshlab
- `date_to` - Yaratilgan vaqtgacha

**Response:**
```json
{
  "count": 1000,
  "results": [
    {
      "id": 1,
      "agent_code": "AGENT001",
      "agent_name": "Agent Name",
      "latitude": 41.3111,
      "longitude": 69.2797,
      "device_name": "Samsung Galaxy S21",
      "platform": "Android",
      "battery_level": 85.5,
      "network_type": "4G",
      "created_at": "2025-11-26T22:00:00Z"
    }
  ]
}
```

### 2. Yangi agent lokatsiyasi yaratish

**POST** `/api/v1/agent-location/`

**Request Body:**
```json
{
  "agent_code": "AGENT001",
  "latitude": 41.3111,
  "longitude": 69.2797,
  "device_name": "Samsung Galaxy S21",
  "platform": "Android",
  "battery_level": 85.5,
  "network_type": "4G"
}
```

**Required Fields:**
- `agent_code` - Agent kodi
- `latitude` - Latitude
- `longitude` - Longitude

**Optional Fields:**
- Barcha qolgan maydonlar ixtiyoriy (device info, location, network, sensors, battery, security)

---

## Performance va Caching

### Caching

API quyidagi endpointlar uchun caching qo'llaniladi:

- **Project API:**
  - List view: 5 daqiqa cache
  - Detail view: 10 daqiqa cache
  
- **Image Status/Source:**
  - 1 soat cache (kam o'zgaradi)
  
- **Thumbnail API:**
  - 3 daqiqa cache

**Cache Invalidation:**
- Ma'lumotlar o'zgarganda cache avtomatik tozalanadi
- Create, Update, Delete operatsiyalaridan keyin cache invalidate qilinadi

### Background Tasks

1C Integration sync operatsiyalari background'da ishlaydi:

- **Async Processing** - Sync operatsiyalari asinxron ishlaydi
- **Task Status** - `/api/v1/integration/sync/status/{task_id}/` orqali progress kuzatiladi
- **Bulk Operations** - Ko'p yozuvlarni bir vaqtda qayta ishlash
- **Retry Mechanism** - Xatoliklar bo'lganda qayta urinish

### SQLite Optimizations

- **WAL Mode** - Concurrent write operatsiyalar uchun
- **Connection Pooling** - Database connection'lar pool'da saqlanadi
- **Bulk Operations** - `bulk_create` va `bulk_update` ishlatiladi
- **Chunking** - Excel export uchun chunking (SQLite limit muammosini hal qiladi)

---

## Status Kodlar

- `200 OK` - Muvaffaqiyatli so'rov
- `201 Created` - Yangi ma'lumot yaratildi
- `204 No Content` - Muvaffaqiyatli o'chirildi
- `400 Bad Request` - Noto'g'ri so'rov
- `404 Not Found` - Ma'lumot topilmadi
- `500 Internal Server Error` - Server xatosi

## Misollar

### Python (requests)

```python
import requests

# Project yaratish
response = requests.post(
    'http://localhost:8000/api/v1/project/',
    json={
        'code_1c': 'PROJ001',
        'name': 'Yangi Loyiha',
        'description': '<p>Description</p>'
    }
)
print(response.json())

# Rasm yuklash
with open('image.jpg', 'rb') as f:
    response = requests.post(
        'http://localhost:8000/api/v1/project-image/',
        files={'image': f},
        data={'project': 1, 'is_main': True}
    )
print(response.json())
```

### JavaScript (fetch)

```javascript
// Project yaratish
fetch('http://localhost:8000/api/v1/project/', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    code_1c: 'PROJ001',
    name: 'Yangi Loyiha',
    description: '<p>Description</p>'
  })
})
.then(response => response.json())
.then(data => console.log(data));

// Rasm yuklash
const formData = new FormData();
formData.append('project', 1);
formData.append('image', fileInput.files[0]);
formData.append('is_main', true);

fetch('http://localhost:8000/api/v1/project-image/', {
  method: 'POST',
  body: formData
})
.then(response => response.json())
.then(data => console.log(data));
```

### cURL

```bash
# Project yaratish
curl -X POST http://localhost:8000/api/v1/project/ \
  -H "Content-Type: application/json" \
  -d '{
    "code_1c": "PROJ001",
    "name": "Yangi Loyiha",
    "description": "<p>Description</p>"
  }'

# Rasm yuklash
curl -X POST http://localhost:8000/api/v1/project-image/ \
  -F "project=1" \
  -F "image=@image.jpg" \
  -F "is_main=true"
```

