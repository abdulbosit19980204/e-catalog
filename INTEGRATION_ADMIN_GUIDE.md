# Integration Admin Qo'llanmasi

Django Admin orqali Integration sozlamalarini boshqarish qo'llanmasi.

## 📋 Integration Yaratish

### 1. Django Admin'ga kirish

```
http://localhost:8000/admin/
```

### 2. Integration yaratish

1. **Integration** bo'limiga o'ting
2. **Add Integration** tugmasini bosing
3. Quyidagi ma'lumotlarni to'ldiring:

#### Asosiy ma'lumotlar

- **Name** - Integration nomi
  - Masalan: "1C Main Integration", "1C Test Integration"
  - Har bir integration uchun unique bo'lishi kerak

- **Project** - Qaysi project'ga tegishli
  - Dropdown'dan project tanlang
  - Agar project yo'q bo'lsa, avval Project yaratish kerak

- **Description** - Integration tavsifi (ixtiyoriy)
  - Rich text editor orqali formatlash mumkin

#### 1C Web Service sozlamalari

- **WSDL URL** - 1C Web Service WSDL URL
  - Masalan: `http://192.168.0.111/EVYAP_TEST2/EVYAP_TEST2.1cws?wsdl`
  - To'liq URL bo'lishi kerak

- **Method Nomenklatura** - Nomenklatura'larni olish uchun method nomi
  - Default: `GetProductList`
  - 1C API da qanday method nomi bo'lsa, shuni yozing

- **Method Clients** - Client'larni olish uchun method nomi
  - Default: `GetClientList`
  - 1C API da qanday method nomi bo'lsa, shuni yozing

- **Chunk Size** - Bir vaqtda qancha ma'lumot yuklash
  - Default: 100
  - Katta hajmdagi ma'lumotlar uchun 50-200 orasida
  - Kichik hajmdagi ma'lumotlar uchun 200-500 orasida

#### Status

- **Is Active** - Integration faolmi?
  - Faqat active integration'lar ishlatiladi

- **Is Deleted** - Integration o'chirilganmi?
  - Soft delete uchun

### 3. Saqlash

**Save** tugmasini bosing.

## 🔍 Integration Log'larni ko'rish

### 1. Integration Log bo'limiga o'tish

**Integration Logs** bo'limiga o'ting.

### 2. Log'larni ko'rish

Har bir sync operatsiyasi uchun log yaratiladi:

- **Integration** - Qaysi integration
- **Sync Type** - Nomenklatura yoki Clients
- **Status** - Fetching, Processing, Completed, Error
- **Progress** - Total, Processed, Created, Updated, Errors
- **Progress Percent** - Foizda progress
- **Error Message** - Xato bo'lsa, xato xabari
- **Started At** - Qachon boshlangan
- **Completed At** - Qachon tugagan

### 3. Log tafsilotlarini ko'rish

Log'ga bosib, batafsil ma'lumotlarni ko'ring.

## 📊 Integration misollari

### Misol 1: Asosiy Integration

```
Name: 1C Main Integration
Project: Main Project
WSDL URL: http://192.168.0.111/EVYAP_TEST2/EVYAP_TEST2.1cws?wsdl
Method Nomenklatura: GetProductList
Method Clients: GetClientList
Chunk Size: 100
```

### Misol 2: Test Integration

```
Name: 1C Test Integration
Project: Test Project
WSDL URL: http://192.168.0.111/EVYAP_TEST/EVYAP_TEST.1cws?wsdl
Method Nomenklatura: GetProductList
Method Clients: GetClientList
Chunk Size: 50
```

## 🔄 Sync operatsiyalari

### API orqali sync

Integration yaratilgandan keyin, API orqali sync qilish mumkin:

```bash
POST /api/v1/integration/sync/nomenklatura/{integration_id}/
POST /api/v1/integration/sync/clients/{integration_id}/
```

### Integration ID ni topish

Django Admin'da Integration ro'yxatida ID ko'rsatiladi yoki Integration tafsilotlarida URL'da ko'rsatiladi.

## ⚠️ Muhim eslatmalar

1. **WSDL URL** - To'g'ri URL bo'lishi kerak
2. **Method nomlari** - 1C API ga mos bo'lishi kerak
3. **Project** - Integration yaratilishdan oldin project yaratilishi kerak
4. **Chunk Size** - Katta hajmdagi ma'lumotlar uchun kichikroq (50-100)
5. **Is Active** - Faqat active integration'lar ishlatiladi

## 🔍 Troubleshooting

### Integration ishlamayapti

1. WSDL URL ni tekshiring
2. Method nomlarini tekshiring
3. Integration active ekanligini tekshiring
4. Log'larni ko'ring

### Xatolar

1. Integration Log bo'limiga o'ting
2. Error status'dagi log'larni ko'ring
3. Error Message'ni o'qing
4. WSDL URL va method nomlarini tekshiring

