import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from nomenklatura.models import Nomenklatura
from django.db.models import Count

duplicates = Nomenklatura.objects.filter(is_deleted=False).values('code_1c').annotate(count=Count('code_1c')).filter(count__gt=1)
for d in duplicates:
    print(f"Code: {d['code_1c']}, Count: {d['count']}")
    nodes = Nomenklatura.objects.filter(code_1c=d['code_1c'], is_deleted=False)
    for n in nodes:
        print(f"  ID: {n.id}, Project: {n.project.name if n.project else 'None'}, Name: {n.name}")
