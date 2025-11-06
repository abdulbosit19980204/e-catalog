# Integratsiya Qo'llanmasi

E-Catalog Microservice'ni boshqa servicelar bilan integratsiya qilish bo'yicha qo'llanma.

## 🔗 API Endpoint'lar

### Base URL
```
Production: https://api.your-domain.com/api/v1/
Development: http://localhost:8000/api/v1/
```

### Asosiy Endpoint'lar

#### Project API
- `GET /api/v1/project/` - Barcha project'lar
- `POST /api/v1/project/` - Yangi project yaratish
- `GET /api/v1/project/{code_1c}/` - Bitta project
- `PUT /api/v1/project/{code_1c}/` - Project yangilash
- `PATCH /api/v1/project/{code_1c}/` - Project qisman yangilash
- `DELETE /api/v1/project/{code_1c}/` - Project o'chirish (soft delete)

#### Client API
- `GET /api/v1/client/` - Barcha client'lar
- `POST /api/v1/client/` - Yangi client yaratish
- `GET /api/v1/client/{client_code_1c}/` - Bitta client
- `PUT /api/v1/client/{client_code_1c}/` - Client yangilash
- `PATCH /api/v1/client/{client_code_1c}/` - Client qisman yangilash
- `DELETE /api/v1/client/{client_code_1c}/` - Client o'chirish (soft delete)

#### Nomenklatura API
- `GET /api/v1/nomenklatura/` - Barcha nomenklatura'lar
- `POST /api/v1/nomenklatura/` - Yangi nomenklatura yaratish
- `GET /api/v1/nomenklatura/{code_1c}/` - Bitta nomenklatura
- `PUT /api/v1/nomenklatura/{code_1c}/` - Nomenklatura yangilash
- `PATCH /api/v1/nomenklatura/{code_1c}/` - Nomenklatura qisman yangilash
- `DELETE /api/v1/nomenklatura/{code_1c}/` - Nomenklatura o'chirish (soft delete)

## 🔐 Authentication

### Token Olish

```bash
POST /api/token/
Content-Type: application/json

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

### Token Yangilash

```bash
POST /api/token/refresh/
Content-Type: application/json

{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

### Token bilan So'rov

```bash
GET /api/v1/project/
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc...
Content-Type: application/json
```

## 🌐 CORS Configuration

Boshqa servicelar bilan integratsiya uchun CORS sozlamalari:

### Environment Variable

```bash
# .env faylida
CORS_ALLOWED_ORIGINS=https://frontend-service.com,https://api-gateway.com,https://another-service.com
```

### Settings

```python
# config/settings.py
CORS_ALLOWED_ORIGINS = [
    "https://frontend-service.com",
    "https://api-gateway.com",
    "https://another-service.com",
]
CORS_ALLOW_CREDENTIALS = True
```

## 📝 Integratsiya Misollari

### Python Service

```python
import requests

API_BASE_URL = "https://api.your-domain.com/api/v1/"
TOKEN_URL = "https://api.your-domain.com/api/token/"

class ECatalogClient:
    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.token = None
        self.refresh_token = None
    
    def authenticate(self):
        """Token olish"""
        response = requests.post(TOKEN_URL, json={
            'username': self.username,
            'password': self.password
        })
        data = response.json()
        self.token = data['access']
        self.refresh_token = data['refresh']
        return self.token
    
    def get_headers(self):
        """Authorization header bilan headers"""
        return {
            'Authorization': f'Bearer {self.token}',
            'Content-Type': 'application/json',
        }
    
    def get_projects(self, search=None, code_1c=None):
        """Project'lar ro'yxatini olish"""
        params = {}
        if search:
            params['search'] = search
        if code_1c:
            params['code_1c'] = code_1c
        
        response = requests.get(
            f'{API_BASE_URL}project/',
            headers=self.get_headers(),
            params=params
        )
        return response.json()
    
    def create_project(self, code_1c, name, title=None, description=None):
        """Yangi project yaratish"""
        data = {
            'code_1c': code_1c,
            'name': name,
        }
        if title:
            data['title'] = title
        if description:
            data['description'] = description
        
        response = requests.post(
            f'{API_BASE_URL}project/',
            headers=self.get_headers(),
            json=data
        )
        return response.json()
    
    def upload_project_image(self, project_id, image_path, is_main=False):
        """Project rasm yuklash"""
        with open(image_path, 'rb') as f:
            files = {'image': f}
            data = {
                'project': project_id,
                'is_main': is_main
            }
            headers = {'Authorization': f'Bearer {self.token}'}
            response = requests.post(
                f'{API_BASE_URL}project-image/',
                headers=headers,
                files=files,
                data=data
            )
        return response.json()

# Foydalanish
client = ECatalogClient('username', 'password')
client.authenticate()
projects = client.get_projects(search='test')
```

### JavaScript/TypeScript Service

```typescript
class ECatalogClient {
  private baseUrl: string;
  private token: string | null = null;
  private refreshToken: string | null = null;

  constructor(baseUrl: string) {
    this.baseUrl = baseUrl;
  }

  async authenticate(username: string, password: string): Promise<void> {
    const response = await fetch(`${this.baseUrl}../token/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ username, password }),
    });
    const data = await response.json();
    this.token = data.access;
    this.refreshToken = data.refresh;
  }

  private getHeaders(): HeadersInit {
    return {
      'Authorization': `Bearer ${this.token}`,
      'Content-Type': 'application/json',
    };
  }

  async getProjects(search?: string, code1c?: string): Promise<any> {
    const params = new URLSearchParams();
    if (search) params.append('search', search);
    if (code1c) params.append('code_1c', code1c);

    const response = await fetch(
      `${this.baseUrl}project/?${params.toString()}`,
      { headers: this.getHeaders() }
    );
    return response.json();
  }

  async createProject(data: {
    code_1c: string;
    name: string;
    title?: string;
    description?: string;
  }): Promise<any> {
    const response = await fetch(`${this.baseUrl}project/`, {
      method: 'POST',
      headers: this.getHeaders(),
      body: JSON.stringify(data),
    });
    return response.json();
  }

  async uploadProjectImage(
    projectId: number,
    imageFile: File,
    isMain: boolean = false
  ): Promise<any> {
    const formData = new FormData();
    formData.append('project', projectId.toString());
    formData.append('image', imageFile);
    formData.append('is_main', isMain.toString());

    const response = await fetch(`${this.baseUrl}project-image/`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${this.token}`,
      },
      body: formData,
    });
    return response.json();
  }
}

// Foydalanish
const client = new ECatalogClient('https://api.your-domain.com/api/v1/');
await client.authenticate('username', 'password');
const projects = await client.getProjects('test');
```

### Node.js Service

```javascript
const axios = require('axios');
const FormData = require('form-data');
const fs = require('fs');

class ECatalogClient {
  constructor(baseUrl) {
    this.baseUrl = baseUrl;
    this.token = null;
    this.refreshToken = null;
  }

  async authenticate(username, password) {
    const response = await axios.post(`${this.baseUrl}../token/`, {
      username,
      password,
    });
    this.token = response.data.access;
    this.refreshToken = response.data.refresh;
    return this.token;
  }

  getHeaders() {
    return {
      'Authorization': `Bearer ${this.token}`,
      'Content-Type': 'application/json',
    };
  }

  async getProjects(search, code1c) {
    const params = {};
    if (search) params.search = search;
    if (code1c) params.code_1c = code1c;

    const response = await axios.get(`${this.baseUrl}project/`, {
      headers: this.getHeaders(),
      params,
    });
    return response.data;
  }

  async createProject(data) {
    const response = await axios.post(
      `${this.baseUrl}project/`,
      data,
      { headers: this.getHeaders() }
    );
    return response.data;
  }

  async uploadProjectImage(projectId, imagePath, isMain = false) {
    const form = new FormData();
    form.append('project', projectId);
    form.append('image', fs.createReadStream(imagePath));
    form.append('is_main', isMain);

    const response = await axios.post(
      `${this.baseUrl}project-image/`,
      form,
      {
        headers: {
          ...form.getHeaders(),
          'Authorization': `Bearer ${this.token}`,
        },
      }
    );
    return response.data;
  }
}

// Foydalanish
const client = new ECatalogClient('https://api.your-domain.com/api/v1/');
await client.authenticate('username', 'password');
const projects = await client.getProjects('test');
```

## 🔄 Rate Limiting

- **Anonim foydalanuvchilar**: 100 so'rov/soat
- **Autentifikatsiya qilingan**: 1000 so'rov/soat

Agar limitdan oshib ketsangiz, quyidagi xato qaytadi:
```json
{
  "detail": "Request was throttled. Expected available in X seconds."
}
```

## 📊 Response Format

### Muvaffaqiyatli Response
```json
{
  "id": 1,
  "code_1c": "PROJ001",
  "name": "Project Name",
  "description": "<p>Description</p>",
  "images": [
    {
      "id": 1,
      "image": "/media/projects/image.jpg",
      "image_url": "https://api.your-domain.com/media/projects/image.jpg",
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

## 🔍 Search va Filtering

### Search
```bash
GET /api/v1/project/?search=test
```

### Filtering
```bash
GET /api/v1/project/?code_1c=PROJ001&name=Test
```

### Ordering
```bash
GET /api/v1/project/?ordering=-created_at
```

### Pagination
```bash
GET /api/v1/project/?page=2&page_size=50
```

## ✅ Production'ga Qo'yish

1. **Environment Variables** sozlang
2. **CORS_ALLOWED_ORIGINS** ni boshqa servicelar manzillari bilan to'ldiring
3. **ALLOWED_HOSTS** ni to'ldiring
4. **DEBUG=False** qiling
5. **SECRET_KEY** ni kuchli qiling
6. **HTTPS** ishlatish

## 📞 Yordam

Agar muammo bo'lsa:
1. API dokumentatsiyani ko'ring: `/api/docs/` yoki `/api/redoc/`
2. Loglarni tekshiring
3. Health check qiling: `GET /api/v1/`

