"""
Script to generate descriptions for Nomenklatura and Client models using AI.
This script uses OpenAI API to generate descriptions based on names.

Usage:
    python manage.py shell < scripts/generate_descriptions.py
    OR
    python scripts/generate_descriptions.py

Environment variables:
    OPENAI_API_KEY - Your OpenAI API key (required)
    OPENAI_MODEL - Model to use (default: gpt-3.5-turbo)
"""

import os
import sys
import django
from django.conf import settings

# Setup Django
if not settings.configured:
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
    django.setup()

from nomenklatura.models import Nomenklatura
from client.models import Client
from django.db import transaction
import time

# Try to import openai
try:
    import openai
except ImportError:
    print("ERROR: openai package not installed. Install it with: pip install openai")
    sys.exit(1)

# Configuration
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
OPENAI_MODEL = os.environ.get('OPENAI_MODEL', 'gpt-3.5-turbo')

if not OPENAI_API_KEY:
    print("ERROR: OPENAI_API_KEY environment variable is not set!")
    print("Please set it with: export OPENAI_API_KEY='your-api-key'")
    sys.exit(1)

# Initialize OpenAI client
client = openai.OpenAI(api_key=OPENAI_API_KEY)


def generate_description(name, title=None, item_type="nomenklatura"):
    """
    Generate description using OpenAI API based on name and title.
    
    Args:
        name: Item name
        title: Optional title
        item_type: Type of item ('nomenklatura' or 'client')
    
    Returns:
        Generated description as HTML string
    """
    try:
        # Build prompt based on item type
        if item_type == "nomenklatura":
            prompt = f"""Quyidagi mahsulot nomi asosida professional va batafsil tavsif yozing (HTML formatida, <p> teglarida).
Mahsulot nomi: {name}
{f"Mahsulot sarlavhasi: {title}" if title else ""}

Tavsif quyidagilarni o'z ichiga olishi kerak:
- Mahsulotning asosiy xususiyatlari
- Foydalanish sohasi
- Afzalliklari
- Texnik xususiyatlari (agar mavjud bo'lsa)

Tavsif professional, aniq va qiziqarli bo'lishi kerak. HTML formatida yozing, <p> teglaridan foydalaning."""
        else:  # client
            prompt = f"""Quyidagi mijoz nomi asosida professional va batafsil tavsif yozing (HTML formatida, <p> teglarida).
Mijoz nomi: {name}

Tavsif quyidagilarni o'z ichiga olishi kerak:
- Mijozning faoliyat sohasi
- Xizmatlar yoki mahsulotlar
- Biznes modeli
- Qisqacha tarix yoki maqsadlar (agar mavjud bo'lsa)

Tavsif professional, aniq va qiziqarli bo'lishi kerak. HTML formatida yozing, <p> teglaridan foydalaning."""

        # Call OpenAI API
        response = client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[
                {"role": "system", "content": "Siz professional mahsulot va mijoz tavsiflarini yozuvchi mutaxassissiz. HTML formatida javob bering."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=500,
        )
        
        description = response.choices[0].message.content.strip()
        
        # Ensure it's valid HTML
        if not description.startswith('<'):
            description = f"<p>{description}</p>"
        
        return description
        
    except Exception as e:
        print(f"  ❌ Xatolik: {str(e)}")
        return None


def generate_nomenklatura_descriptions(dry_run=False, limit=None):
    """
    Generate descriptions for all Nomenklatura items that don't have descriptions.
    
    Args:
        dry_run: If True, only show what would be updated without saving
        limit: Maximum number of items to process (None for all)
    """
    print("\n" + "="*60)
    print("NOMENKLATURA DESCRIPTIONS GENERATION")
    print("="*60)
    
    # Get items without descriptions
    queryset = Nomenklatura.objects.filter(
        is_deleted=False,
        is_active=True
    ).filter(
        models.Q(description__isnull=True) | models.Q(description='') | models.Q(description='<p><br></p>')
    )
    
    if limit:
        queryset = queryset[:limit]
    
    total = queryset.count()
    print(f"\n📊 Topildi: {total} ta nomenklatura (description yo'q)")
    
    if total == 0:
        print("✅ Barcha nomenklaturalarda description mavjud!")
        return
    
    if dry_run:
        print("\n🔍 DRY RUN MODE - Hech narsa saqlanmaydi\n")
    
    updated = 0
    failed = 0
    
    for idx, item in enumerate(queryset, 1):
        print(f"\n[{idx}/{total}] {item.name} (Code: {item.code_1c})")
        
        description = generate_description(item.name, item.title, "nomenklatura")
        
        if description:
            if not dry_run:
                try:
                    with transaction.atomic():
                        item.description = description
                        item.save(update_fields=['description', 'updated_at'])
                    print(f"  ✅ Description yozildi")
                    updated += 1
                except Exception as e:
                    print(f"  ❌ Saqlashda xatolik: {str(e)}")
                    failed += 1
            else:
                print(f"  ✅ Description tayyor (dry run)")
                updated += 1
        else:
            failed += 1
        
        # Rate limiting - avoid API rate limits
        time.sleep(0.5)  # 0.5 second delay between requests
    
    print("\n" + "="*60)
    print(f"✅ Muvaffaqiyatli: {updated}")
    print(f"❌ Xatoliklar: {failed}")
    print(f"📊 Jami: {total}")
    print("="*60)


def generate_client_descriptions(dry_run=False, limit=None):
    """
    Generate descriptions for all Client items that don't have descriptions.
    
    Args:
        dry_run: If True, only show what would be updated without saving
        limit: Maximum number of items to process (None for all)
    """
    print("\n" + "="*60)
    print("CLIENT DESCRIPTIONS GENERATION")
    print("="*60)
    
    # Get items without descriptions
    queryset = Client.objects.filter(
        is_deleted=False,
        is_active=True
    ).filter(
        models.Q(description__isnull=True) | models.Q(description='') | models.Q(description='<p><br></p>')
    )
    
    if limit:
        queryset = queryset[:limit]
    
    total = queryset.count()
    print(f"\n📊 Topildi: {total} ta client (description yo'q)")
    
    if total == 0:
        print("✅ Barcha clientlarda description mavjud!")
        return
    
    if dry_run:
        print("\n🔍 DRY RUN MODE - Hech narsa saqlanmaydi\n")
    
    updated = 0
    failed = 0
    
    for idx, item in enumerate(queryset, 1):
        print(f"\n[{idx}/{total}] {item.name} (Code: {item.client_code_1c})")
        if item.email:
            print(f"  📧 Email: {item.email}")
        if item.phone:
            print(f"  📞 Phone: {item.phone}")
        
        description = generate_description(item.name, None, "client")
        
        if description:
            if not dry_run:
                try:
                    with transaction.atomic():
                        item.description = description
                        item.save(update_fields=['description', 'updated_at'])
                    print(f"  ✅ Description yozildi")
                    updated += 1
                except Exception as e:
                    print(f"  ❌ Saqlashda xatolik: {str(e)}")
                    failed += 1
            else:
                print(f"  ✅ Description tayyor (dry run)")
                updated += 1
        else:
            failed += 1
        
        # Rate limiting - avoid API rate limits
        time.sleep(0.5)  # 0.5 second delay between requests
    
    print("\n" + "="*60)
    print(f"✅ Muvaffaqiyatli: {updated}")
    print(f"❌ Xatoliklar: {failed}")
    print(f"📊 Jami: {total}")
    print("="*60)


def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Generate descriptions for Nomenklatura and Client models')
    parser.add_argument('--dry-run', action='store_true', help='Test mode - do not save changes')
    parser.add_argument('--nomenklatura', action='store_true', help='Generate for Nomenklatura only')
    parser.add_argument('--client', action='store_true', help='Generate for Client only')
    parser.add_argument('--limit', type=int, help='Limit number of items to process (for testing)')
    
    args = parser.parse_args()
    
    print("\n" + "="*60)
    print("AI DESCRIPTION GENERATOR")
    print("="*60)
    print(f"Model: {OPENAI_MODEL}")
    print(f"Dry Run: {args.dry_run}")
    print("="*60)
    
    if not args.nomenklatura and not args.client:
        # Generate for both
        generate_nomenklatura_descriptions(dry_run=args.dry_run, limit=args.limit)
        generate_client_descriptions(dry_run=args.dry_run, limit=args.limit)
    else:
        if args.nomenklatura:
            generate_nomenklatura_descriptions(dry_run=args.dry_run, limit=args.limit)
        if args.client:
            generate_client_descriptions(dry_run=args.dry_run, limit=args.limit)
    
    print("\n✅ Barcha operatsiyalar yakunlandi!\n")


if __name__ == '__main__':
    # Fix import for models.Q
    from django.db import models
    main()

