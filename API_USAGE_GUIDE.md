# API Foydalanish Qo'llanmasi

Bu qo'llanmada E-Catalog Microservice API'laridan foydalanishning to'liq ketma-ketligi va misollari keltirilgan.

## 📋 Mundarija

1. [Boshlash](#boshlash)
2. [Authentication](#authentication)
3. [Project API](#project-api)
4. [Client API](#client-api)
5. [Nomenklatura API](#nomenklatura-api)
6. [Integration API](#integration-api)
7. [Excel Import/Export](#excel-importexport)
8. [AI Description Generator](#ai-description-generator)
9. [Thumbnail API](#thumbnail-api)
10. [Agent Location API](#agent-location-api)
11. [Xatoliklar bilan ishlash](#xatoliklar-bilan-ishlash)

---

## Boshlash

### 1. Base URL

Barcha API so'rovlari quyidagi base URL'dan boshlanadi:

```
http://localhost:8000/api/v1/
```

### 2. Content-Type

Barcha so'rovlar `application/json` formatida yuboriladi va qabul qilinadi.

### 3. Authentication

**Muhim:** Client API'lariga kirish uchun authentication talab qilinadi. Boshqa API'lar (Project, Nomenklatura) public bo'lishi mumkin.

---

## Authentication

### 1. Token olish

**POST** `/api/token/`

**Request Body:**
```json
{
  "username": "your_username",
  "password": "your_password"
}
```

**Response:**
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

**cURL misoli:**
```bash
curl -X POST http://localhost:8000/api/token/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "password": "admin123"
  }'
```

**Python misoli:**
```python
import requests

response = requests.post(
    'http://localhost:8000/api/token/',
    json={
        'username': 'admin',
        'password': 'admin123'
    }
)

data = response.json()
access_token = data['access']
refresh_token = data['refresh']
```

**JavaScript misoli:**
```javascript
const response = await fetch('http://localhost:8000/api/token/', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    username: 'admin',
    password: 'admin123'
  })
});

const data = await response.json();
const accessToken = data.access;
const refreshToken = data.refresh;
```

### 2. Token yangilash

**POST** `/api/token/refresh/`

**Request Body:**
```json
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

**Response:**
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

**Python misoli:**
```python
response = requests.post(
    'http://localhost:8000/api/token/refresh/',
    json={'refresh': refresh_token}
)

new_access_token = response.json()['access']
```

### 3. Token tekshirish

**POST** `/api/token/verify/`

**Request Body:**
```json
{
  "token": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

**Response:**
```json
{}  # Token to'g'ri bo'lsa
```

---

## Project API

### 1. Barcha Project'larni olish

**GET** `/api/v1/project/`

**Authentication:** Talab qilinmaydi

**Query Parameters:**
- `search` - Qidirish (code_1c, name, title maydonlarida)
- `code_1c` - Kod bo'yicha filtrlash
- `name` - Nom bo'yicha filtrlash
- `ordering` - Tartiblash (masalan: `-created_at`)
- `page` - Sahifa raqami

**Python misoli:**
```python
import requests

# Oddiy so'rov
response = requests.get('http://localhost:8000/api/v1/project/')
projects = response.json()

# Qidirish bilan
response = requests.get(
    'http://localhost:8000/api/v1/project/',
    params={'search': 'test'}
)

# Filtrlash va tartiblash
response = requests.get(
    'http://localhost:8000/api/v1/project/',
    params={
        'code_1c': 'PROJ001',
        'ordering': '-created_at',
        'page': 1
    }
)
```

**JavaScript misoli:**
```javascript
// Oddiy so'rov
const response = await fetch('http://localhost:8000/api/v1/project/');
const projects = await response.json();

// Qidirish bilan
const searchResponse = await fetch(
  'http://localhost:8000/api/v1/project/?search=test'
);
const searchResults = await searchResponse.json();

// Filtrlash va tartiblash
const params = new URLSearchParams({
  code_1c: 'PROJ001',
  ordering: '-created_at',
  page: 1
});
const filteredResponse = await fetch(
  `http://localhost:8000/api/v1/project/?${params}`
);
const filteredResults = await filteredResponse.json();
```

### 2. Bitta Project olish

**GET** `/api/v1/project/{code_1c}/`

**Python misoli:**
```python
response = requests.get('http://localhost:8000/api/v1/project/PROJ001/')
project = response.json()
```

### 3. Yangi Project yaratish

**POST** `/api/v1/project/`

**Authentication:** Talab qilinadi (JWT token)

**Request Body:**
```json
{
  "code_1c": "PROJ001",
  "name": "Yangi Project",
  "title": "Project Sarlavhasi",
  "description": "<p>Project haqida ma'lumot</p>",
  "is_active": true
}
```

**Python misoli:**
```python
headers = {
    'Authorization': f'Bearer {access_token}',
    'Content-Type': 'application/json'
}

data = {
    'code_1c': 'PROJ001',
    'name': 'Yangi Project',
    'title': 'Project Sarlavhasi',
    'description': '<p>Project haqida ma\'lumot</p>',
    'is_active': True
}

response = requests.post(
    'http://localhost:8000/api/v1/project/',
    headers=headers,
    json=data
)

if response.status_code == 201:
    project = response.json()
    print(f"Project yaratildi: {project['name']}")
```

**JavaScript misoli:**
```javascript
const response = await fetch('http://localhost:8000/api/v1/project/', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${accessToken}`,
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    code_1c: 'PROJ001',
    name: 'Yangi Project',
    title: 'Project Sarlavhasi',
    description: '<p>Project haqida ma\'lumot</p>',
    is_active: true
  })
});

if (response.ok) {
  const project = await response.json();
  console.log('Project yaratildi:', project.name);
}
```

### 4. Project yangilash

**PUT** `/api/v1/project/{code_1c}/` - To'liq yangilash
**PATCH** `/api/v1/project/{code_1c}/` - Qisman yangilash

**Python misoli:**
```python
headers = {
    'Authorization': f'Bearer {access_token}',
    'Content-Type': 'application/json'
}

data = {
    'name': 'Yangilangan Nom',
    'description': '<p>Yangilangan description</p>'
}

response = requests.patch(
    'http://localhost:8000/api/v1/project/PROJ001/',
    headers=headers,
    json=data
)
```

### 5. Project o'chirish

**DELETE** `/api/v1/project/{code_1c}/`

**Python misoli:**
```python
headers = {
    'Authorization': f'Bearer {access_token}'
}

response = requests.delete(
    'http://localhost:8000/api/v1/project/PROJ001/',
    headers=headers
)

if response.status_code == 204:
    print("Project o'chirildi")
```

---

## Client API

**Muhim:** Client API'lariga kirish uchun authentication **majburiy**.

### 1. Barcha Client'larni olish

**GET** `/api/v1/client/`

**Authentication:** Majburiy (JWT token)

**Python misoli:**
```python
headers = {
    'Authorization': f'Bearer {access_token}'
}

response = requests.get(
    'http://localhost:8000/api/v1/client/',
    headers=headers
)

clients = response.json()
```

**JavaScript misoli:**
```javascript
const response = await fetch('http://localhost:8000/api/v1/client/', {
  headers: {
    'Authorization': `Bearer ${accessToken}`
  }
});

if (response.status === 401) {
  // Token eskirgan, yangilash kerak
  // ...
}

const clients = await response.json();
```

### 2. Yangi Client yaratish

**POST** `/api/v1/client/`

**Request Body:**
```json
{
  "client_code_1c": "CLI001",
  "name": "Yangi Client",
  "email": "client@example.com",
  "phone": "+998901234567",
  "description": "<p>Client haqida ma'lumot</p>"
}
```

**Python misoli:**
```python
headers = {
    'Authorization': f'Bearer {access_token}',
    'Content-Type': 'application/json'
}

data = {
    'client_code_1c': 'CLI001',
    'name': 'Yangi Client',
    'email': 'client@example.com',
    'phone': '+998901234567',
    'description': '<p>Client haqida ma\'lumot</p>'
}

response = requests.post(
    'http://localhost:8000/api/v1/client/',
    headers=headers,
    json=data
)
```

---

## Nomenklatura API

### 1. Barcha Nomenklatura'larni olish

**GET** `/api/v1/nomenklatura/`

**Authentication:** Talab qilinmaydi

**Python misoli:**
```python
response = requests.get('http://localhost:8000/api/v1/nomenklatura/')
nomenklatura = response.json()
```

### 2. Yangi Nomenklatura yaratish

**POST** `/api/v1/nomenklatura/`

**Authentication:** Talab qilinadi

**Request Body:**
```json
{
  "code_1c": "NOM001",
  "name": "Yangi Nomenklatura",
  "title": "Nomenklatura Sarlavhasi",
  "description": "<p>Nomenklatura haqida ma'lumot</p>"
}
```

---

## Integration API

### 1. Nomenklatura Sync

**POST** `/api/v1/integration/sync/nomenklatura/{integration_id}/`

**Authentication:** Majburiy

**Python misoli:**
```python
headers = {
    'Authorization': f'Bearer {access_token}'
}

response = requests.post(
    'http://localhost:8000/api/v1/integration/sync/nomenklatura/1/',
    headers=headers
)

data = response.json()
task_id = data['task_id']
print(f"Sync boshlandi. Task ID: {task_id}")
```

### 2. Clients Sync

**POST** `/api/v1/integration/sync/clients/{integration_id}/`

**Python misoli:**
```python
response = requests.post(
    'http://localhost:8000/api/v1/integration/sync/clients/1/',
    headers=headers
)

data = response.json()
task_id = data['task_id']
```

### 3. Sync Status olish

**GET** `/api/v1/integration/sync/status/{task_id}/`

**Python misoli:**
```python
import time

task_id = "abc123-def456-..."

while True:
    response = requests.get(
        f'http://localhost:8000/api/v1/integration/sync/status/{task_id}/',
        headers=headers
    )
    
    status = response.json()
    print(f"Status: {status['status']}")
    print(f"Progress: {status['progress_percent']}%")
    print(f"Processed: {status['processed']} / {status['total']}")
    
    if status['status'] in ['completed', 'error']:
        break
    
    time.sleep(2)  # 2 soniyada bir marta tekshirish
```

**JavaScript misoli:**
```javascript
const taskId = 'abc123-def456-...';

const checkStatus = async () => {
  const response = await fetch(
    `http://localhost:8000/api/v1/integration/sync/status/${taskId}/`,
    {
      headers: {
        'Authorization': `Bearer ${accessToken}`
      }
    }
  );
  
  const status = await response.json();
  console.log('Status:', status.status);
  console.log('Progress:', status.progress_percent + '%');
  console.log('Processed:', status.processed, '/', status.total);
  
  if (status.status === 'processing' || status.status === 'fetching') {
    setTimeout(checkStatus, 2000);  // 2 soniyadan keyin qayta tekshirish
  }
};

checkStatus();
```

---

## Xatoliklar bilan ishlash

### 1. Authentication xatoliklari

**401 Unauthorized:**
```json
{
  "detail": "Authentication credentials were not provided."
}
```

**Yechim:**
```python
if response.status_code == 401:
    # Token yangilash yoki qayta login qilish
    new_token = refresh_token(refresh_token)
    # So'rovni qayta yuborish
```

### 2. Validation xatoliklari

**400 Bad Request:**
```json
{
  "code_1c": ["This field is required."],
  "name": ["This field may not be blank."]
}
```

**Yechim:**
```python
if response.status_code == 400:
    errors = response.json()
    for field, messages in errors.items():
        print(f"{field}: {', '.join(messages)}")
```

### 3. Not Found xatoliklari

**404 Not Found:**
```json
{
  "detail": "Not found."
}
```

**Yechim:**
```python
if response.status_code == 404:
    print("Ma'lumot topilmadi")
```

### 4. Rate Limit xatoliklari

**429 Too Many Requests:**
```json
{
  "detail": "Request was throttled. Expected available in 60 seconds."
}
```

**Yechim:**
```python
if response.status_code == 429:
    retry_after = int(response.headers.get('Retry-After', 60))
    print(f"Rate limit. {retry_after} soniyadan keyin qayta urinib ko'ring")
    time.sleep(retry_after)
```

---

## To'liq Python misoli

```python
import requests
import time

# 1. Token olish
def get_token(username, password):
    response = requests.post(
        'http://localhost:8000/api/token/',
        json={'username': username, 'password': password}
    )
    return response.json()

# 2. Client yaratish
def create_client(access_token, client_data):
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    response = requests.post(
        'http://localhost:8000/api/v1/client/',
        headers=headers,
        json=client_data
    )
    return response.json()

# 3. Integration sync
def sync_nomenklatura(access_token, integration_id):
    headers = {'Authorization': f'Bearer {access_token}'}
    response = requests.post(
        f'http://localhost:8000/api/v1/integration/sync/nomenklatura/{integration_id}/',
        headers=headers
    )
    return response.json()

# 4. Status kuzatish
def check_sync_status(access_token, task_id):
    headers = {'Authorization': f'Bearer {access_token}'}
    response = requests.get(
        f'http://localhost:8000/api/v1/integration/sync/status/{task_id}/',
        headers=headers
    )
    return response.json()

# Asosiy kod
if __name__ == '__main__':
    # Login
    tokens = get_token('admin', 'admin123')
    access_token = tokens['access']
    
    # Client yaratish
    client = create_client(access_token, {
        'client_code_1c': 'CLI001',
        'name': 'Test Client',
        'email': 'test@example.com'
    })
    print(f"Client yaratildi: {client['name']}")
    
    # Integration sync
    sync_result = sync_nomenklatura(access_token, 1)
    task_id = sync_result['task_id']
    print(f"Sync boshlandi: {task_id}")
    
    # Status kuzatish
    while True:
        status = check_sync_status(access_token, task_id)
        print(f"Progress: {status['progress_percent']}%")
        
        if status['status'] in ['completed', 'error']:
            break
        
        time.sleep(2)
```

---

## To'liq JavaScript misoli

```javascript
// 1. Token olish
async function getToken(username, password) {
  const response = await fetch('http://localhost:8000/api/token/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ username, password })
  });
  return await response.json();
}

// 2. Client yaratish
async function createClient(accessToken, clientData) {
  const response = await fetch('http://localhost:8000/api/v1/client/', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${accessToken}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(clientData)
  });
  return await response.json();
}

// 3. Integration sync
async function syncNomenklatura(accessToken, integrationId) {
  const response = await fetch(
    `http://localhost:8000/api/v1/integration/sync/nomenklatura/${integrationId}/`,
    {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${accessToken}`
      }
    }
  );
  return await response.json();
}

// 4. Status kuzatish
async function checkSyncStatus(accessToken, taskId) {
  const response = await fetch(
    `http://localhost:8000/api/v1/integration/sync/status/${taskId}/`,
    {
      headers: {
        'Authorization': `Bearer ${accessToken}`
      }
    }
  );
  return await response.json();
}

// Asosiy kod
(async () => {
  // Login
  const tokens = await getToken('admin', 'admin123');
  const accessToken = tokens.access;
  
  // Client yaratish
  const client = await createClient(accessToken, {
    client_code_1c: 'CLI001',
    name: 'Test Client',
    email: 'test@example.com'
  });
  console.log('Client yaratildi:', client.name);
  
  // Integration sync
  const syncResult = await syncNomenklatura(accessToken, 1);
  const taskId = syncResult.task_id;
  console.log('Sync boshlandi:', taskId);
  
  // Status kuzatish
  const checkStatus = async () => {
    const status = await checkSyncStatus(accessToken, taskId);
    console.log('Progress:', status.progress_percent + '%');
    
    if (status.status === 'processing' || status.status === 'fetching') {
      setTimeout(checkStatus, 2000);
    }
  };
  
  checkStatus();
})();
```

---

## Excel Import/Export

### Project Excel Export

**GET** `/api/v1/project/export-xlsx/`

**Misol:**
```bash
curl -X GET "http://localhost:8000/api/v1/project/export-xlsx/?search=test" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -o projects.xlsx
```

**JavaScript:**
```javascript
async function exportProjects(accessToken, filters = {}) {
  const params = new URLSearchParams(filters);
  const response = await fetch(
    `http://localhost:8000/api/v1/project/export-xlsx/?${params}`,
    {
      headers: {
        'Authorization': `Bearer ${accessToken}`
      }
    }
  );
  const blob = await response.blob();
  const url = window.URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = 'projects.xlsx';
  a.click();
}
```

### Project Excel Import

**POST** `/api/v1/project/import-xlsx/`

**Misol:**
```bash
curl -X POST "http://localhost:8000/api/v1/project/import-xlsx/" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@projects.xlsx"
```

**JavaScript:**
```javascript
async function importProjects(accessToken, file) {
  const formData = new FormData();
  formData.append('file', file);
  
  const response = await fetch(
    'http://localhost:8000/api/v1/project/import-xlsx/',
    {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${accessToken}`
      },
      body: formData
    }
  );
  return await response.json();
}
```

**Response:**
```json
{
  "created": 10,
  "updated": 5,
  "errors": []
}
```

### Client va Nomenklatura Excel

Xuddi shu formatda:
- `/api/v1/client/export-xlsx/`
- `/api/v1/client/import-xlsx/`
- `/api/v1/nomenklatura/export-xlsx/`
- `/api/v1/nomenklatura/import-xlsx/`

---

## AI Description Generator

### Foydalanish

**Test qilish (dry-run):**
```bash
python manage.py generate_descriptions --nomenklatura --dry-run --limit 5
```

**Haqiqiy ishlatish:**
```bash
# Nomenklatura uchun
python manage.py generate_descriptions --nomenklatura

# Client uchun
python manage.py generate_descriptions --client

# Ikkalasi uchun
python manage.py generate_descriptions
```

### Environment Variables

```bash
export OPENAI_API_KEY="your-api-key-here"
export OPENAI_MODEL="gpt-3.5-turbo"  # Optional, default: gpt-3.5-turbo
```

Batafsil ma'lumot: [scripts/README_DESCRIPTIONS.md](../scripts/README_DESCRIPTIONS.md)

---

## Thumbnail API

### Barcha thumbnail rasmlar

**GET** `/api/v1/thumbnails/`

**Query Parameters:**
- `entity_type` - `project`, `client`, `nomenklatura`
- `is_main` - `true` yoki `false`
- `status` - Rasm statusi

**Misol:**
```javascript
async function getThumbnails(accessToken, entityType = null) {
  const params = entityType ? `?entity_type=${entityType}` : '';
  const response = await fetch(
    `http://localhost:8000/api/v1/thumbnails/${params}`,
    {
      headers: {
        'Authorization': `Bearer ${accessToken}`
      }
    }
  );
  return await response.json();
}
```

### Entity-specific thumbnails

- `/api/v1/thumbnails/projects/` - Faqat Project
- `/api/v1/thumbnails/clients/` - Faqat Client
- `/api/v1/thumbnails/nomenklatura/` - Faqat Nomenklatura

---

## Agent Location API

### Agent lokatsiyasi yaratish

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

**Misol:**
```javascript
async function createAgentLocation(accessToken, locationData) {
  const response = await fetch(
    'http://localhost:8000/api/v1/agent-location/',
    {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${accessToken}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(locationData)
    }
  );
  return await response.json();
}
```

### Agent lokatsiyalari ro'yxati

**GET** `/api/v1/agent-location/`

**Query Parameters:**
- `agent_code` - Agent kodi
- `region` - Hudud
- `platform` - `Android` yoki `iOS`
- `device_id` - Qurilma ID
- `date_from` - Yaratilgan vaqtdan boshlab
- `date_to` - Yaratilgan vaqtgacha

---

## Qo'shimcha ma'lumotlar

- **API Documentation (Swagger)**: http://localhost:8000/api/docs/
- **ReDoc**: http://localhost:8000/api/redoc/
- **OpenAPI Schema**: http://localhost:8000/api/schema/
- **AI Description Generator**: [scripts/README_DESCRIPTIONS.md](../scripts/README_DESCRIPTIONS.md)

