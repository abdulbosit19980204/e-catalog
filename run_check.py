import os
import sys

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
import django
django.setup()

from django.core.management import call_command

with open('check_errors_final.txt', 'w') as f:
    try:
        call_command('check', stdout=f, stderr=f)
    except Exception as e:
        f.write(str(e))
