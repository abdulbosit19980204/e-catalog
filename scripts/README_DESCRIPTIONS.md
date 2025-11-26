# AI Description Generator

Bu script Nomenklatura va Client modellariga AI yordamida professional descriptionlar yozadi.

## O'rnatish

1. **OpenAI paketini o'rnating:**
   ```bash
   pip install openai
   ```

2. **OpenAI API key oling:**
   - [OpenAI Platform](https://platform.openai.com/) ga kiring
   - API key yarating
   - Environment variable sifatida o'rnating:
     ```bash
     # Windows (PowerShell)
     $env:OPENAI_API_KEY="your-api-key-here"
     
     # Linux/Mac
     export OPENAI_API_KEY="your-api-key-here"
     ```

## Foydalanish

### 1. Test qilish (Dry Run)

Avval test qilib ko'ring, hech narsa saqlanmaydi:

```bash
# Nomenklatura uchun test (5 ta)
python manage.py generate_descriptions --nomenklatura --dry-run --limit 5

# Client uchun test (5 ta)
python manage.py generate_descriptions --client --dry-run --limit 5

# Ikkalasi uchun test
python manage.py generate_descriptions --dry-run --limit 5
```

### 2. Haqiqiy ishlatish

Testdan keyin, barcha itemlar uchun description yozish:

```bash
# Faqat Nomenklatura
python manage.py generate_descriptions --nomenklatura

# Faqat Client
python manage.py generate_descriptions --client

# Ikkalasi uchun
python manage.py generate_descriptions
```

## Parametrlar

- `--dry-run` - Test rejimi, hech narsa saqlanmaydi
- `--nomenklatura` - Faqat Nomenklatura uchun
- `--client` - Faqat Client uchun
- `--limit N` - Faqat N ta itemni qayta ishlash (test uchun)

## Misollar

```bash
# 10 ta nomenklatura uchun test
python manage.py generate_descriptions --nomenklatura --dry-run --limit 10

# Barcha clientlar uchun description yozish
python manage.py generate_descriptions --client

# Barcha nomenklatura va clientlar uchun
python manage.py generate_descriptions
```

## Eslatmalar

- Script har bir so'rov orasida 0.5 soniya kutadi (rate limiting)
- Description HTML formatida yoziladi
- Faqat description yo'q bo'lgan itemlar qayta ishlanadi
- `is_deleted=False` va `is_active=True` bo'lgan itemlar qayta ishlanadi

## Xatoliklar

Agar xatolik bo'lsa:
1. `OPENAI_API_KEY` o'rnatilganligini tekshiring
2. Internet ulanishini tekshiring
3. OpenAI API limitlarini tekshiring

