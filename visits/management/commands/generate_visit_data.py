"""
Management command to generate sample visit data for testing
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import datetime, timedelta
import random
from visits.models import Visit, VisitPlan, VisitImage
from references.models import VisitType, VisitStatus, VisitPriority


class Command(BaseCommand):
    help = 'Test ma\'lumotlari yaratish - tashriflar va rejalar'

    def add_arguments(self, parser):
        parser.add_argument('--visits', type=int, default=50, help='Yaratish uchun tashriflar soni')
        parser.add_argument('--plans', type=int, default=10, help='Yaratish uchun rejalar soni')

    def init_references(self):
        """Ensure reference data exists"""
        self.stdout.write('Referens ma\'lumotlarini tekshirish...')
        
        # Statuses
        statuses = [
            ('SCHEDULED', 'Rejalashtirilgan', '#3B82F6'),
            ('CONFIRMED', 'Tasdiqlangan', '#10B981'),
            ('IN_PROGRESS', 'Jarayonda', '#F59E0B'),
            ('COMPLETED', 'Yakunlangan', '#059669'),
            ('CANCELLED', 'Bekor qilingan', '#EF4444'),
            ('POSTPONED', 'Kechiktirilgan', '#6B7280'),
            ('NO_SHOW', 'Kelmaganlar', '#DC2626'),
        ]
        self.status_map = {}
        for code, name, color in statuses:
            obj, _ = VisitStatus.objects.get_or_create(code=code, defaults={'name': name, 'color': color})
            self.status_map[code] = obj

        # Types
        types = [
            ('PLANNED', 'Rejalashtirilgan'),
            ('UNPLANNED', 'Rejadan tashqari'),
            ('ADDITIONAL', "Qo'shimcha"),
            ('FOLLOW_UP', 'Takroriy tashrif'),
        ]
        self.type_map = {}
        for code, name in types:
            obj, _ = VisitType.objects.get_or_create(code=code, defaults={'name': name})
            self.type_map[code] = obj

        # Priorities
        priorities = [
            ('LOW', 'Past', 1),
            ('MEDIUM', "O'rta", 2),
            ('HIGH', 'Yuqori', 3),
            ('URGENT', 'Shoshilinch', 4),
        ]
        self.priority_map = {}
        for code, name, level in priorities:
            obj, _ = VisitPriority.objects.get_or_create(code=code, defaults={'name': name, 'level': level})
            self.priority_map[code] = obj

    def handle(self, *args, **options):
        num_visits = options['visits']
        num_plans = options['plans']
        
        self.init_references()

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
        ]

        purposes = [
            'Yangi mahsulotlarni taqdim etish', 'Buyurtmalarni qabul qilish', 
            'Mahsulot joylashuvini tekshirish', 'Promostendlarni o\'rnatish',
            'Qarzlarni yig\'ish', 'Yangi shartnoma imzolash'
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
                priority=self.priority_map[random.choice(['LOW', 'MEDIUM', 'HIGH'])],
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
            
            days_offset = random.randint(-30, 10)
            planned_date = timezone.now().date() + timedelta(days=days_offset)
            planned_time = f"{random.randint(9, 17):02d}:{random.randint(0, 59):02d}:00"
            
            if days_offset < -2:
                status_code = random.choice(['COMPLETED', 'COMPLETED', 'CANCELLED', 'NO_SHOW'])
            elif days_offset < 0:
                status_code = random.choice(['COMPLETED', 'IN_PROGRESS'])
            elif days_offset == 0:
                status_code = random.choice(['IN_PROGRESS', 'SCHEDULED', 'CONFIRMED'])
            else:
                status_code = 'SCHEDULED'

            visit_obj = Visit(
                agent_code=agent['code'],
                agent_name=agent['name'],
                agent_phone=agent['phone'],
                client_code=client['code'],
                client_name=client['name'],
                client_address=client['address'],
                visit_type=self.type_map[random.choice(['PLANNED', 'UNPLANNED', 'FOLLOW_UP'])],
                status=self.status_map.get(status_code, self.status_map['SCHEDULED']), # NEW FIELD
                priority=self.priority_map[random.choice(['LOW', 'MEDIUM', 'HIGH'])],
                planned_date=planned_date,
                planned_time=planned_time,
                planned_duration_minutes=random.choice([30, 45, 60]),
                purpose=random.choice(purposes),
            )

            # Add actual times
            if status_code in ['COMPLETED', 'IN_PROGRESS']:
                start_time = datetime.combine(planned_date, datetime.strptime(planned_time, '%H:%M:%S').time())
                start_time = timezone.make_aware(start_time)
                visit_obj.actual_start_time = start_time
                visit_obj.check_in_latitude = 41.3111 + random.uniform(-0.05, 0.05)
                visit_obj.check_in_longitude = 69.2797 + random.uniform(-0.05, 0.05)
                visit_obj.check_in_accuracy = random.uniform(5, 20)
                visit_obj.check_in_address = client['address']

            if status_code == 'COMPLETED':
                duration = random.randint(20, 90)
                visit_obj.actual_end_time = visit_obj.actual_start_time + timedelta(minutes=duration)
                visit_obj.duration = timedelta(minutes=duration)
                visit_obj.check_out_latitude = visit_obj.check_in_latitude
                visit_obj.check_out_longitude = visit_obj.check_in_longitude
                visit_obj.outcome = 'Muvaffaqiyatli'
                visit_obj.client_satisfaction = random.randint(3, 5)

            if status_code == 'CANCELLED':
                visit_obj.cancelled_reason = 'Sabab...'
                visit_obj.cancelled_by = agent['name']
                visit_obj.cancelled_at = timezone.now()

            visit_obj.save()
            visits_created += 1
            
            # Images
            if status_code == 'COMPLETED' and random.random() > 0.7:
                VisitImage.objects.create(
                    visit=visit_obj,
                    image_type='PRODUCT',
                    image_url='https://via.placeholder.com/150',
                    latitude=visit_obj.check_in_latitude,
                    longitude=visit_obj.check_in_longitude
                )

        self.stdout.write(self.style.SUCCESS(f'✓ {visits_created} ta tashrif yaratildi'))
        
        # Statistics
        total_visits = Visit.objects.filter(is_deleted=False).count()
        completed = Visit.objects.filter(status__code='COMPLETED', is_deleted=False).count()
        in_progress = Visit.objects.filter(status__code='IN_PROGRESS', is_deleted=False).count()
        scheduled = Visit.objects.filter(status__code='SCHEDULED', is_deleted=False).count()
        cancelled = Visit.objects.filter(status__code='CANCELLED', is_deleted=False).count()

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

