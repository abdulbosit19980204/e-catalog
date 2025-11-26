"""
Django management command to generate descriptions for Nomenklatura and Client models using AI.

Usage:
    python manage.py generate_descriptions --dry-run --limit 5
    python manage.py generate_descriptions --nomenklatura
    python manage.py generate_descriptions --client
    python manage.py generate_descriptions  # Both

Environment variables:
    OPENAI_API_KEY - Your OpenAI API key (required)
    OPENAI_MODEL - Model to use (default: gpt-3.5-turbo)
"""

from django.core.management.base import BaseCommand
from django.db import models, transaction
from nomenklatura.models import Nomenklatura
from client.models import Client
import os
import time

# Try to import openai
try:
    import openai
except ImportError:
    openai = None


class Command(BaseCommand):
    help = 'Generate descriptions for Nomenklatura and Client models using AI'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Test mode - do not save changes',
        )
        parser.add_argument(
            '--nomenklatura',
            action='store_true',
            help='Generate for Nomenklatura only',
        )
        parser.add_argument(
            '--client',
            action='store_true',
            help='Generate for Client only',
        )
        parser.add_argument(
            '--limit',
            type=int,
            help='Limit number of items to process (for testing)',
        )

    def handle(self, *args, **options):
        # Check if openai is installed
        if openai is None:
            self.stdout.write(
                self.style.ERROR('ERROR: openai package not installed. Install it with: pip install openai')
            )
            return

        # Get configuration
        api_key = os.environ.get('OPENAI_API_KEY')
        model = os.environ.get('OPENAI_MODEL', 'gpt-3.5-turbo')

        if not api_key:
            self.stdout.write(
                self.style.ERROR('ERROR: OPENAI_API_KEY environment variable is not set!')
            )
            self.stdout.write(
                self.style.WARNING('Please set it with: export OPENAI_API_KEY="your-api-key"')
            )
            return

        # Initialize OpenAI client
        client = openai.OpenAI(api_key=api_key)

        self.stdout.write(self.style.SUCCESS('\n' + '='*60))
        self.stdout.write(self.style.SUCCESS('AI DESCRIPTION GENERATOR'))
        self.stdout.write(self.style.SUCCESS('='*60))
        self.stdout.write(f'Model: {model}')
        self.stdout.write(f'Dry Run: {options["dry_run"]}')
        self.stdout.write('='*60 + '\n')

        if not options['nomenklatura'] and not options['client']:
            # Generate for both
            self.generate_nomenklatura_descriptions(
                client, model, options['dry_run'], options['limit']
            )
            self.generate_client_descriptions(
                client, model, options['dry_run'], options['limit']
            )
        else:
            if options['nomenklatura']:
                self.generate_nomenklatura_descriptions(
                    client, model, options['dry_run'], options['limit']
                )
            if options['client']:
                self.generate_client_descriptions(
                    client, model, options['dry_run'], options['limit']
                )

        self.stdout.write(self.style.SUCCESS('\n✅ Barcha operatsiyalar yakunlandi!\n'))

    def generate_description(self, client, model, name, title=None, item_type="nomenklatura"):
        """Generate description using OpenAI API"""
        try:
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

            response = client.chat.completions.create(
                model=model,
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
            self.stdout.write(self.style.ERROR(f'  ❌ Xatolik: {str(e)}'))
            return None

    def generate_nomenklatura_descriptions(self, client, model, dry_run=False, limit=None):
        """Generate descriptions for Nomenklatura items"""
        self.stdout.write('\n' + '='*60)
        self.stdout.write('NOMENKLATURA DESCRIPTIONS GENERATION')
        self.stdout.write('='*60)

        queryset = Nomenklatura.objects.filter(
            is_deleted=False,
            is_active=True
        ).filter(
            models.Q(description__isnull=True) | 
            models.Q(description='') | 
            models.Q(description='<p><br></p>')
        )

        if limit:
            queryset = queryset[:limit]

        total = queryset.count()
        self.stdout.write(f'\n📊 Topildi: {total} ta nomenklatura (description yo\'q)')

        if total == 0:
            self.stdout.write(self.style.SUCCESS('✅ Barcha nomenklaturalarda description mavjud!'))
            return

        if dry_run:
            self.stdout.write(self.style.WARNING('\n🔍 DRY RUN MODE - Hech narsa saqlanmaydi\n'))

        updated = 0
        failed = 0

        for idx, item in enumerate(queryset, 1):
            self.stdout.write(f'\n[{idx}/{total}] {item.name} (Code: {item.code_1c})')

            description = self.generate_description(client, model, item.name, item.title, "nomenklatura")

            if description:
                if not dry_run:
                    try:
                        with transaction.atomic():
                            item.description = description
                            item.save(update_fields=['description', 'updated_at'])
                        self.stdout.write(self.style.SUCCESS('  ✅ Description yozildi'))
                        updated += 1
                    except Exception as e:
                        self.stdout.write(self.style.ERROR(f'  ❌ Saqlashda xatolik: {str(e)}'))
                        failed += 1
                else:
                    self.stdout.write(self.style.SUCCESS('  ✅ Description tayyor (dry run)'))
                    updated += 1
            else:
                failed += 1

            # Rate limiting
            time.sleep(0.5)

        self.stdout.write('\n' + '='*60)
        self.stdout.write(f'✅ Muvaffaqiyatli: {updated}')
        self.stdout.write(f'❌ Xatoliklar: {failed}')
        self.stdout.write(f'📊 Jami: {total}')
        self.stdout.write('='*60)

    def generate_client_descriptions(self, client, model, dry_run=False, limit=None):
        """Generate descriptions for Client items"""
        self.stdout.write('\n' + '='*60)
        self.stdout.write('CLIENT DESCRIPTIONS GENERATION')
        self.stdout.write('='*60)

        queryset = Client.objects.filter(
            is_deleted=False,
            is_active=True
        ).filter(
            models.Q(description__isnull=True) | 
            models.Q(description='') | 
            models.Q(description='<p><br></p>')
        )

        if limit:
            queryset = queryset[:limit]

        total = queryset.count()
        self.stdout.write(f'\n📊 Topildi: {total} ta client (description yo\'q)')

        if total == 0:
            self.stdout.write(self.style.SUCCESS('✅ Barcha clientlarda description mavjud!'))
            return

        if dry_run:
            self.stdout.write(self.style.WARNING('\n🔍 DRY RUN MODE - Hech narsa saqlanmaydi\n'))

        updated = 0
        failed = 0

        for idx, item in enumerate(queryset, 1):
            self.stdout.write(f'\n[{idx}/{total}] {item.name} (Code: {item.client_code_1c})')
            if item.email:
                self.stdout.write(f'  📧 Email: {item.email}')
            if item.phone:
                self.stdout.write(f'  📞 Phone: {item.phone}')

            description = self.generate_description(client, model, item.name, None, "client")

            if description:
                if not dry_run:
                    try:
                        with transaction.atomic():
                            item.description = description
                            item.save(update_fields=['description', 'updated_at'])
                        self.stdout.write(self.style.SUCCESS('  ✅ Description yozildi'))
                        updated += 1
                    except Exception as e:
                        self.stdout.write(self.style.ERROR(f'  ❌ Saqlashda xatolik: {str(e)}'))
                        failed += 1
                else:
                    self.stdout.write(self.style.SUCCESS('  ✅ Description tayyor (dry run)'))
                    updated += 1
            else:
                failed += 1

            # Rate limiting
            time.sleep(0.5)

        self.stdout.write('\n' + '='*60)
        self.stdout.write(f'✅ Muvaffaqiyatli: {updated}')
        self.stdout.write(f'❌ Xatoliklar: {failed}')
        self.stdout.write(f'📊 Jami: {total}')
        self.stdout.write('='*60)

