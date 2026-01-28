import os
import django
import google.generativeai as genai

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecatalog.settings')
django.setup()

from utils.settings import get_system_setting

api_key = get_system_setting('GEMINI_API_KEY')
if not api_key:
    print("Error: GEMINI_API_KEY not found in settings")
    exit(1)

genai.configure(api_key=api_key)

results = []
test_model = 'models/gemini-2.5-flash'
prompt = """
Internetdan quyidagi mahsulot haqida ma'lumot toping (o'z bilimingizga tayanib): iPhone 15 Pro 256GB Natural Titanium

Sizdan 2 ta narsa talab qilinadi:
1. Mahsulot Tavsifi (HTML formatida).
2. Mahsulot Xususiyatlari (JSON formatida).

JSON keys: brand, model, color, material, weight, dimensions, category.
Faqat JSON va HTML qaytaring.
"""

print(f"Testing {test_model} knowledge...")
try:
    model = genai.GenerativeModel(model_name=test_model)
    res = model.generate_content(prompt)
    print("SUCCESS!")
    print(res.text[:200])
    results.append(res.text)
except Exception as e:
    print(f"FAILED: {e}")

with open('results_utf8.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(results))
