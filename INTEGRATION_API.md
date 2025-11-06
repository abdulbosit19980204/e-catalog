# Integration API Documentation

1C dan ma'lumotlarni yuklab olish uchun Integration API.

## 🔗 Base URL

```
/api/v1/integration/
```

## 📋 Endpoint'lar

### 1. Nomenklatura'larni 1C dan yuklab olish

**Endpoint:** `POST /api/v1/integration/sync/nomenklatura/{integration_id}/`

**Authentication:** Required (JWT Token)

**Description:** 1C dan nomenklatura'larni yuklab olish. Integration sozlamalariga asosan sync qilinadi. 10 minglab nomenklatura yuklanganda ham service osilib qolmaydi, chunki:
- Async processing (background thread)
- Chunk processing (integration sozlamasiga asosan)
- Progress tracking (database'da saqlanadi)
- Transaction safety
- Project'ga tegishli ma'lumotlarni ajratish

**Request:**
```bash
POST /api/v1/integration/sync/nomenklatura/1/
Authorization: Bearer YOUR_TOKEN
Content-Type: application/json
```

**Parameters:**
- `integration_id` - Integration ID (Django admin'da yaratilgan)

**Response (202 Accepted):**
```json
{
  "task_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "started",
  "message": "Nomenklatura sync started in background"
}
```

**Progress Check:**
```bash
GET /api/v1/integration/sync/status/{task_id}/
Authorization: Bearer YOUR_TOKEN
```

**Progress Response:**
```json
{
  "status": "processing",
  "total": 10000,
  "processed": 3500,
  "created": 2000,
  "updated": 1500,
  "errors": 0,
  "progress_percent": 35
}
```

**Status Values:**
- `fetching` - 1C dan ma'lumotlar olinmoqda
- `processing` - Ma'lumotlar saqlanmoqda
- `completed` - Bajarildi
- `error` - Xato yuz berdi

### 2. Client'larni 1C dan yuklab olish

**Endpoint:** `POST /api/v1/integration/sync/clients/{integration_id}/`

**Authentication:** Required (JWT Token)

**Description:** 1C dan client'larni yuklab olish. Integration sozlamalariga asosan sync qilinadi. Async processing va chunk processing bilan.

**Request:**
```bash
POST /api/v1/integration/sync/clients/1/
Authorization: Bearer YOUR_TOKEN
Content-Type: application/json
```

**Parameters:**
- `integration_id` - Integration ID (Django admin'da yaratilgan)

**Response (202 Accepted):**
```json
{
  "task_id": "550e8400-e29b-41d4-a716-446655440001",
  "status": "started",
  "message": "Clients sync started in background"
}
```

### 3. Sync Status

**Endpoint:** `GET /api/v1/integration/sync/status/{task_id}/`

**Authentication:** Required (JWT Token)

**Description:** Sync progress'ni olish

**Request:**
```bash
GET /api/v1/integration/sync/status/550e8400-e29b-41d4-a716-446655440000/
Authorization: Bearer YOUR_TOKEN
```

**Response (200 OK):**
```json
{
  "status": "completed",
  "total": 10000,
  "processed": 10000,
  "created": 5000,
  "updated": 5000,
  "errors": 0,
  "progress_percent": 100
}
```

**Error Response (404 Not Found):**
```json
{
  "error": "Task not found"
}
```

## 🔧 Features

### 1. Async Processing
- Barcha sync operatsiyalar background thread'da ishlaydi
- Service osilib qolmaydi
- 10 minglab ma'lumotlar yuklanganda ham tez javob qaytaradi

### 2. Chunk Processing
- Ma'lumotlar 100 ta chunk'larga bo'linadi
- Har bir chunk alohida transaction'da ishlaydi
- Database yuki kamayadi

### 3. Progress Tracking
- Real-time progress tracking
- `task_id` orqali progress'ni kuzatish mumkin
- Status, created, updated, errors sonlari

### 4. Error Handling
- Xatolar log'ga yoziladi
- Progress'da error count ko'rsatiladi
- Service osilib qolmaydi

### 5. Transaction Safety
- Har bir chunk transaction'da ishlaydi
- Xato bo'lsa rollback qilinadi
- Data integrity saqlanadi

## 📝 Usage Examples

### Python Example

```python
import requests
import time

API_BASE = "https://api.your-domain.com/api/v1/integration"
TOKEN = "YOUR_JWT_TOKEN"

headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}

# Nomenklatura'larni yuklab olish
response = requests.post(
    f"{API_BASE}/sync/nomenklatura/",
    headers=headers
)
task_id = response.json()["task_id"]

# Progress'ni kuzatish
while True:
    status_response = requests.get(
        f"{API_BASE}/sync/status/{task_id}/",
        headers=headers
    )
    status = status_response.json()
    
    print(f"Progress: {status['progress_percent']}%")
    print(f"Processed: {status['processed']}/{status['total']}")
    print(f"Created: {status['created']}, Updated: {status['updated']}")
    
    if status['status'] in ['completed', 'error']:
        break
    
    time.sleep(2)  # 2 soniyada bir marta tekshirish
```

### JavaScript Example

```javascript
const API_BASE = 'https://api.your-domain.com/api/v1/integration';
const TOKEN = 'YOUR_JWT_TOKEN';

async function syncNomenklatura() {
  // Sync boshlash
  const response = await fetch(`${API_BASE}/sync/nomenklatura/`, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${TOKEN}`,
      'Content-Type': 'application/json',
    },
  });
  
  const { task_id } = await response.json();
  
  // Progress'ni kuzatish
  const checkProgress = async () => {
    const statusResponse = await fetch(
      `${API_BASE}/sync/status/${task_id}/`,
      {
        headers: {
          'Authorization': `Bearer ${TOKEN}`,
        },
      }
    );
    
    const status = await statusResponse.json();
    
    console.log(`Progress: ${status.progress_percent}%`);
    console.log(`Processed: ${status.processed}/${status.total}`);
    
    if (status.status === 'completed' || status.status === 'error') {
      console.log('Sync completed!');
      return;
    }
    
    // 2 soniyada bir marta tekshirish
    setTimeout(checkProgress, 2000);
  };
  
  checkProgress();
}
```

## ⚙️ Configuration

### Django Admin orqali Integration sozlash

1. Django Admin'ga kirish: `/admin/`
2. **Integration** bo'limiga o'tish
3. **Add Integration** tugmasini bosing
4. Quyidagi ma'lumotlarni to'ldiring:
   - **Name** - Integration nomi (masalan: "1C Main Integration")
   - **Project** - Qaysi project'ga tegishli
   - **WSDL URL** - 1C Web Service WSDL URL (masalan: `http://192.168.0.111/EVYAP_TEST2/EVYAP_TEST2.1cws?wsdl`)
   - **Method Nomenklatura** - Nomenklatura'larni olish uchun method nomi (default: `GetProductList`)
   - **Method Clients** - Client'larni olish uchun method nomi (default: `GetClientList`)
   - **Chunk Size** - Bir vaqtda qancha ma'lumot yuklash (default: 100)
   - **Description** - Integration tavsifi (ixtiyoriy)

### Integration sozlamalari

Har bir integration uchun:
- **WSDL URL** - 1C Web Service URL
- **Method nomlari** - 1C API method nomlari
- **Chunk Size** - Bir vaqtda yuklash uchun chunk hajmi
- **Project** - Qaysi project'ga tegishli

### Project'ga tegishli ma'lumotlar

- Agar 1C dan `Project` maydoni kelsa, u project topiladi yoki yaratiladi
- Agar `Project` maydoni bo'lmasa, integration'ning project'i ishlatiladi
- Barcha ma'lumotlar integration'ning project'iga tegishli deb belgilanadi

## 🔍 Monitoring

### Logs

Barcha xatolar Django log'ga yoziladi:

```python
logger.error(f"Error fetching nomenklatura from 1C: {e}")
```

### Progress Storage

Hozircha progress dictionary'da saqlanadi. Production'da Redis yoki database ishlatish tavsiya etiladi.

## ⚠️ Important Notes

1. **Authentication Required** - Barcha endpoint'lar JWT token talab qiladi
2. **Background Processing** - Sync operatsiyalar background'da ishlaydi
3. **Progress Tracking** - `task_id` orqali progress'ni kuzatish mumkin
4. **Chunk Size** - Katta chunk size database yukini oshiradi
5. **1C Connection** - 1C Web Service mavjud bo'lishi kerak
6. **Error Handling** - Xatolar log'ga yoziladi va progress'da ko'rsatiladi

## 🚀 Production Recommendations

1. **Redis** - Progress tracking uchun Redis ishlatish
2. **Celery** - Background tasks uchun Celery ishlatish
3. **Monitoring** - Progress va error'larni monitoring qilish
4. **Rate Limiting** - 1C API ga so'rovlar sonini cheklash
5. **Retry Logic** - Xato bo'lsa qayta urinish mexanizmi

