# E-Catalog Ma'lumotlar Bazasi Sxemasi (Detailed Database Schema)

Ushbu hujjat loyihadagi barcha modellar, ularning fieldlari (maydonlari), turlari va o'zaro bog'liqliklarini (relationships) to'liq tavsiflaydi.

---

## 1. Umumiy (BaseModel)
Deyarli barcha modellar quyidagi fieldlarga ega:
*   `is_active` (Boolean): Ma'lumot faolligi.
*   `is_deleted` (Boolean): Soft-delete bayrog'i.
*   `created_at` (DateTimeField): Yaratilgan vaqt.
*   `updated_at` (DateTimeField): Oxirgi yangilangan vaqt.

---

## 2. Foydalanuvchilar va Loyihalar (Users & Projects)

### AuthProject (`users.AuthProject`)
1C integratsiyasi va loyiha sozlamalarini saqlaydi.
*   `name` (String): Loyiha nomi.
*   `project_code` (String): Unikal kod (1C bilan mos).
*   `wsdl_url` (URL): Asosiy 1C servisi.
*   `wsdl_url_alt` (URL): Zaxira 1C servisi.
*   **Bog'lanishlar**: `visits`, `user_profiles` va `visit_steps` ga linklangan.

### UserProfile (`users.UserProfile`)
Django standart `User` modelini biznes mantiqi bilan bog'laydi.
*   `user` (OneToOne): Standart User modeli bilan bog'liqlik.
*   `project` (ForeignKey): `AuthProject`ga bog'langan.
*   `code_1c` (String): Agentning 1C dagi kodi.
*   `code_sklad` (String): Ombor kodi.

### Project (`api.Project`)
Biznes ma'lumotlarining asosi.
*   `code_1c` (String): Unikal 1C kodi.
*   `name` (String): Nomi.
*   `description` (RichText): Batafsil ma'lumot.

---

## 3. Kataloglar (Product & Client Catalogs)

### Client (`client.Client`)
*   `project` (ForeignKey): `Project`ga bog'langan.
*   `client_code_1c` (String): 1C kodi.
*   `name` (String): Client nomi.
*   `tax_id` (String): INN/STIR.
*   `legal_address` (Text): Yuridik manzil.
*   `rating` (Decimal): Mijoz reytingi.

### Nomenklatura (`nomenklatura.Nomenklatura`)
*   `project` (ForeignKey): `Project`ga bog'langan.
*   `code_1c` (String): 1C kodi.
*   `sku` / `article_code` / `barcode` (String): Mahsulot kodlari.
*   `base_price` (Decimal): Asosiy narx.
*   `stock_quantity` (Decimal): Qoldiq miqdori.

---

## 4. Tashriflar va Tracking (Visits & GPS)

### Visit (`visits.Visit`)
Tizimning eng murakkab va faol modeli.
*   `visit_id` (UUID): Unikal ID.
*   `agent` (ForeignKey): `UserProfile`ga bog'langan.
*   `client` (ForeignKey): `Client`ga bog'langan.
*   `visit_type` / `status` / `priority` (ForeignKey): Dinamik lug'atlarga bog'lanish.
*   `planned_date` (Date): Rejalashtirilgan sana.
*   `actual_start_time` / `actual_end_time` (DateTime): Check-in va Check-out vaqtlari.
*   `duration` (Duration): Tashrif davomiyligi.
*   `check_in_latitude/longitude` (Decimal): GPS koordinatalar.

### VisitStepResult (`visits.VisitStepResult`)
Tashrif davomida bajarilgan topshiriqlar.
*   `visit` (ForeignKey): Tegishli tashrif.
*   `step` (ForeignKey): `VisitStep` (Tashrif qadami).
*   `value_text` / `value_number` / `value_photo`: Natija qiymati.

### AgentLocation (`api.AgentLocation`)
*   `agent_code` (String): Agent kodi.
*   `latitude / longitude` (Decimal): GPS nuqtasi.
*   `battery_level` (Decimal): Batareya quvvati.
*   `device_info`: Qurilma haqidagi batafsil texnik ma'lumotlar.

---

## 5. Dinamik Ma'lumotnomalar (References)
Bu modellar tizimni o'zgartirmasdan, uning ishlash mantig'ini sozlash imkonini beradi:
*   **VisitType**: Tashrif turlari (Market-Visit, Audit va b.).
*   **VisitStatus**: Statuslar (SCHEDULED, IN_PROGRESS, COMPLETED).
*   **VisitStep**: Har bir tashrif turi uchun bajarilishi lozim bo'lgan qadamlar (Checklist).

---

## 6. Rasmlar Tizimi (Image Management)
Barcha rasm modellari (`ProjectImage`, `ClientImage`, `NomenklaturaImage`, `VisitImage`) quyidagilarga ega:
*   `image` (ImageField): Original fayl.
*   `image_sm/md/lg/thumbnail`: Avtomatik generatsiya qilinadigan turli o'lchamlar.
*   `is_main` (Boolean): Asosiy rasm.
*   `status` (ForeignKey): `ImageStatus` (Verified, Pending).
*   `source` (ForeignKey): `ImageSource` (Agent, System, Admin).

---

## 7. Integratsiya va Chat (Integration & Communication)

### Integration (`integration.Integration`)
*   `wsdl_url` / `username` / `password`: 1C SOAP ulanish ma'lumotlari.
*   `method_nomenklatura` / `method_clients`: SOAP methodlar nomlari.

### Conversation & ChatMessage (`chat.models`)
*   `conversation`: Foydalanuvchi va Admin o'rtasidagi suhbat.
*   `body` (Text): Xabar matni.
*   `image / file` (FileField): Biriktirilgan fayllar.

---

## 8. Loglar va Monitoring (Logs)
*   **ImportLog**: Excel importlar tarixi (`created_count`, `error_count`).
*   **IntegrationLog**: 1C sync tarixi (`task_id`, `status`, `processed_items`).
*   **ErrorLog**: Tizimdagi barcha xatoliklar, stack-trace va request ma'lumotlari.
