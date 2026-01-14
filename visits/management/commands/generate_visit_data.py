"""
Management command to generate sample visit data for testing
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import datetime, timedelta
import random
from visits.models import Visit, VisitPlan, VisitImage, VisitType, VisitStatus, VisitPriority


class Command(BaseCommand):
    help = 'Test ma\'lumotlari yaratish - tashriflar va rejalar'

    def add_arguments(self, parser):
        parser.add_argument(
            '--visits',
            type=int,
            default=50,
            help='Yaratish uchun tashriflar soni'
        )
        parser.add_argument(
            '--plans',
            type=int,
            default=10,
            help='Yaratish uchun rejalar soni'
        )

    def handle(self, *args, **options):
        num_visits = options['visits']
        num_plans = options['plans']

        self.stdout.write(self.style.SUCCESS(f'Test ma\'lumotlari yaratilmoqda...'))

        # Sample data
        agents = [
            {'code': 'AGT001', 'name': 'Abbos Rahimov', 'phone': '+998901234567'},
            {'code': 'AGT002', 'name': 'Bobur Karimov', 'phone': '+998901234568'},
            {'code': 'AGT003', 'name': 'Dilshod Toshmatov', 'phone': '+998901234569'},
            {'code': 'AGT004', 'name': 'Ergash Saidov', 'phone': '+998901234570'},
            {'code': 'AGT005', 'name': 'Farrux Nazarov', 'phone': '+998901234571'},
        ]

        clients = [
            {'code': 'CLI001', 'name': 'Samarqand Savdo Markazi', 'address': 'Samarqand sh., Registon ko\'chasi 15'},
            {'code': 'CLI002', 'name': 'Toshkent Mega Market', 'address': 'Toshkent sh., Amir Temur 45'},
            {'code': 'CLI003', 'name': 'Buxoro Supermarket', 'address': 'Buxoro sh., Mustaqillik 23'},
            {'code': 'CLI004', 'name': 'Andijon Do\'kon', 'address': 'Andijon sh., Bobur 12'},
            {'code': 'CLI005', 'name': 'Namangan Bozori', 'address': 'Namangan sh., Navbahor 78'},
            {'code': 'CLI006', 'name': 'Farg\'ona Magazin', 'address': 'Farg\'ona sh., Al-Farg\'oniy 34'},
            {'code': 'CLI007', 'name': 'Qarshi Market', 'address': 'Qarshi sh., Nasaf 56'},
            {'code': 'CLI008', 'name': 'Guliston Savdo', 'address': 'Guliston sh., Mustaqillik 90'},
        ]

        purposes = [
            'Yangi mahsulotlarni taqdim etish',
            'Buyurtmalarni qabul qilish',
            'Mahsulot joylashuvini tekshirish',
            'Promostendlarni o\'rnatish',
            'Qarzlarni yig\'ish',
            'Yangi shartnoma imzolash',
            'Inventarizatsiya o\'tkazish',
            'Marketing materiallari tarqatish',
        ]

        outcomes = [
            'Muvaffaqiyatli buyurtma olindi - 5 mln',
            'Yangi mahsulotlar joyga qo\'yildi',
            'Promostendlar o\'rnatildi, reklama boshlandi',
            'Klient bilan shartnoma uzaytirildi',
            'Qarz qisman to\'landi - 2 mln',
            'Inventarizatsiya yakunlandi - 95% to\'g\'ri',
            'Klient bilan yaxshi munosabatlar o\'rnatildi',
        ]

        # Create Visit Plans
        self.stdout.write('Visit rejalarini yaratish...')
        plans_created = 0
        for i in range(num_plans):
            agent = random.choice(agents)
            client = random.choice(clients)
            
            plan = VisitPlan.objects.create(
                agent_code=agent['code'],
                client_code=client['code'],
                frequency=random.choice(['WEEKLY', 'BIWEEKLY', 'MONTHLY']),
                planned_weekday=random.randint(0, 6),
                planned_time=f"{random.randint(9, 17):02d}:00:00",
                duration_minutes=random.choice([30, 45, 60]),
                start_date=timezone.now().date() - timedelta(days=30),
                is_active=True,
                priority=random.choice(['LOW', 'MEDIUM', 'HIGH']),
                auto_generate=True,
                generate_days_ahead=7
            )
            plans_created += 1

        self.stdout.write(self.style.SUCCESS(f'✓ {plans_created} ta reja yaratildi'))

        # Create Visits
        self.stdout.write('Tashriflarni yaratish...')
        visits_created = 0
        
        for i in range(num_visits):
            agent = random.choice(agents)
            client = random.choice(clients)
            
            # Random date in last 30 days or next 10 days
            days_offset = random.randint(-30, 10)
            planned_date = timezone.now().date() + timedelta(days=days_offset)
            planned_time = f"{random.randint(9, 17):02d}:{random.randint(0, 59):02d}:00"
            
            # Determine status based on date
            if days_offset < -2:
                status = random.choice([
                    VisitStatus.COMPLETED,
                    VisitStatus.COMPLETED,
                    VisitStatus.COMPLETED,
                    VisitStatus.CANCELLED,
                    VisitStatus.NO_SHOW
                ])
            elif days_offset < 0:
                status = random.choice([
                    VisitStatus.COMPLETED,
                    VisitStatus.IN_PROGRESS,
                ])
            elif days_offset == 0:
                status = random.choice([
                    VisitStatus.IN_PROGRESS,
                    VisitStatus.SCHEDULED,
                    VisitStatus.CONFIRMED
                ])
            else:
                status = VisitStatus.SCHEDULED

            visit = Visit(
                agent_code=agent['code'],
                agent_name=agent['name'],
                agent_phone=agent['phone'],
                client_code=client['code'],
                client_name=client['name'],
                client_address=client['address'],
                visit_type=random.choice([VisitType.PLANNED, VisitType.PLANNED, VisitType.UNPLANNED, VisitType.FOLLOW_UP]),
                visit_status=status,
                priority=random.choice([VisitPriority.LOW, VisitPriority.MEDIUM, VisitPriority.MEDIUM, VisitPriority.HIGH]),
                planned_date=planned_date,
                planned_time=planned_time,
                planned_duration_minutes=random.choice([30, 45, 60, 90]),
                purpose=random.choice(purposes),
            )

            # Add actual times for completed/in-progress visits
            if status in [VisitStatus.COMPLETED, VisitStatus.IN_PROGRESS]:
                start_time = datetime.combine(planned_date, datetime.strptime(planned_time, '%H:%M:%S').time())
                start_time = timezone.make_aware(start_time)
                visit.actual_start_time = start_time
                
                # GPS coordinates (Tashkent area)
                visit.check_in_latitude = 41.3111 + random.uniform(-0.05, 0.05)
                visit.check_in_longitude = 69.2797 + random.uniform(-0.05, 0.05)
                visit.check_in_accuracy = random.uniform(5, 20)
                visit.check_in_address = client['address']

            # Complete the visit if status is COMPLETED
            if status == VisitStatus.COMPLETED:
                duration = random.randint(20, 90)
                visit.actual_end_time = visit.actual_start_time + timedelta(minutes=duration)
                visit.duration_minutes = duration
                visit.check_out_latitude = visit.check_in_latitude + random.uniform(-0.001, 0.001)
                visit.check_out_longitude = visit.check_in_longitude + random.uniform(-0.001, 0.001)
                visit.outcome = random.choice(outcomes)
                visit.tasks_completed = random.sample([
                    'Mahsulot joylashtirildi',
                    'Promostend o\'rnatildi',
                    'Buyurtma qabul qilindi',
                    'Shartnoma imzolandi',
                    'Reklama materiallari o\'rnatildi'
                ], k=random.randint(1, 3))
                visit.client_satisfaction = random.randint(3, 5)
                
                # Maybe schedule next visit
                if random.random() > 0.5:
                    visit.next_visit_date = planned_date + timedelta(days=random.randint(7, 30))
                    visit.next_visit_notes = 'Keyingi tashrif uchun yangi mahsulotlar tayyorlanadi'

            # Cancel some visits
            if status == VisitStatus.CANCELLED:
                visit.cancelled_reason = random.choice([
                    'Klient band edi',
                    'Ob-havo yomoni',
                    'Agent kasal bo\'lib qoldi',
                    'Klient tashrif vaqtini o\'zgartirdi'
                ])
                visit.cancelled_by = agent['name']
                visit.cancelled_at = timezone.now() - timedelta(hours=random.randint(1, 48))

            visit.save()
            visits_created += 1

            # Add some images to completed visits
            if status == VisitStatus.COMPLETED and random.random() > 0.5:
                num_images = random.randint(1, 4)
                for j in range(num_images):
                    VisitImage.objects.create(
                        visit=visit,
                        image_type=random.choice(['PRODUCT', 'SHELF', 'STOREFRONT', 'RECEIPT']),
                        image_url=f'https://via.placeholder.com/400x300?text=Visit+Image+{j+1}',
                        thumbnail_url=f'https://via.placeholder.com/150x150?text=Thumb+{j+1}',
                        latitude=visit.check_in_latitude,
                        longitude=visit.check_in_longitude,
                        notes=f'Tashrif rasmi {j+1}'
                    )

        self.stdout.write(self.style.SUCCESS(f'✓ {visits_created} ta tashrif yaratildi'))

        # Statistics
        total_visits = Visit.objects.filter(is_deleted=False).count()
        completed = Visit.objects.filter(visit_status=VisitStatus.COMPLETED, is_deleted=False).count()
        in_progress = Visit.objects.filter(visit_status=VisitStatus.IN_PROGRESS, is_deleted=False).count()
        scheduled = Visit.objects.filter(visit_status=VisitStatus.SCHEDULED, is_deleted=False).count()
        cancelled = Visit.objects.filter(visit_status=VisitStatus.CANCELLED, is_deleted=False).count()

        self.stdout.write('\n' + '='*50)
        self.stdout.write(self.style.SUCCESS('TEST MA\'LUMOTLARI TAYYOR!'))
        self.stdout.write('='*50)
        self.stdout.write(f'Jami tashriflar: {total_visits}')
        self.stdout.write(f'  - Yakunlangan: {completed}')
        self.stdout.write(f'  - Jarayonda: {in_progress}')
        self.stdout.write(f'  - Rejalashtirilgan: {scheduled}')
        self.stdout.write(f'  - Bekor qilingan: {cancelled}')
        self.stdout.write(f'\nJami rejalar: {VisitPlan.objects.filter(is_deleted=False).count()}')
        self.stdout.write(f'Jami rasmlar: {VisitImage.objects.filter(is_deleted=False).count()}')
        self.stdout.write('\n' + self.style.SUCCESS('Dashboard test qilishingiz mumkin: /visits'))
