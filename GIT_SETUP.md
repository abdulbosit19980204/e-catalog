# Git Setup Qo'llanmasi

Git repository'ni public repository'ga push qilish uchun qo'llanma.

## 📋 Qadamlar

### 1. Git Repository yaratilgan

```bash
git init
git add .
git commit -m "Initial commit: E-Catalog Microservice with 1C Integration"
```

### 2. GitHub'da yangi repository yaratish

1. GitHub'ga kirish: https://github.com
2. **New repository** tugmasini bosing
3. Repository nomini kiriting (masalan: `e-catalog`)
4. **Public** ni tanlang
5. **Create repository** tugmasini bosing

### 3. Remote Repository qo'shish

GitHub'da repository yaratilgandan keyin, quyidagi buyruqlarni bajaring:

```bash
# Remote repository qo'shish
git remote add origin https://github.com/YOUR_USERNAME/e-catalog.git

# Yoki SSH orqali
git remote add origin git@github.com:YOUR_USERNAME/e-catalog.git
```

**Eslatma:** `YOUR_USERNAME` o'rniga o'zingizning GitHub username'ingizni yozing.

### 4. Branch nomini main ga o'zgartirish

```bash
git branch -M main
```

### 5. Push qilish

```bash
git push -u origin main
```

## 🔄 Keyingi Push'lar

Keyingi o'zgarishlarni push qilish uchun:

```bash
# O'zgarishlarni qo'shish
git add .

# Commit qilish
git commit -m "Your commit message"

# Push qilish
git push
```

## 🔍 Remote Repository'ni tekshirish

```bash
git remote -v
```

## 🔄 Remote Repository'ni o'zgartirish

Agar remote repository URL'ni o'zgartirish kerak bo'lsa:

```bash
# Eski remote'ni olib tashlash
git remote remove origin

# Yangi remote qo'shish
git remote add origin https://github.com/YOUR_USERNAME/NEW_REPO_NAME.git

# Push qilish
git push -u origin main
```

## ⚠️ Muhim Eslatmalar

1. **.env fayl** - `.env` fayl `.gitignore` da, shuning uchun push qilinmaydi
2. **db.sqlite3** - Database fayl `.gitignore` da
3. **venv/** - Virtual environment `.gitignore` da
4. **media/** - Media fayllar `.gitignore` da
5. **SECRET_KEY** - Production'da environment variable sifatida saqlang

## 📝 .gitignore

Quyidagi fayllar va papkalar `.gitignore` da:
- `__pycache__/`
- `*.pyc`
- `venv/`
- `.env`
- `db.sqlite3`
- `media/`
- `staticfiles/`
- `*.log`

## ✅ Checklist

- [ ] Git repository yaratildi
- [ ] Barcha fayllar add qilindi
- [ ] Initial commit qilindi
- [ ] GitHub'da repository yaratildi
- [ ] Remote repository qo'shildi
- [ ] Push qilindi

