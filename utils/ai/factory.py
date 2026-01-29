import logging
from django.conf import settings
from core.models import AIModel
from utils.ai.gemini import GeminiService
from utils.ai.puter import PuterService

logger = logging.getLogger(__name__)

class AIService:
    def __init__(self, model_instance=None):
        if not model_instance:
            # Get default model
            model_instance = AIModel.objects.filter(is_active=True, is_default=True).first() or \
                             AIModel.objects.filter(is_active=True).first()
        
        if not model_instance:
            logger.warning("No active AI model found in database, falling back to default Gemini")
            self.provider = 'google'
            self.model_id = 'models/gemini-2.5-flash'
            self.service = GeminiService()
        else:
            self.provider = model_instance.provider
            self.model_id = model_instance.model_id
            
            if self.provider == 'google':
                self.service = GeminiService()
            elif self.provider == 'puter':
                self.service = PuterService()
            else:
                logger.error(f"Unsupported provider: {self.provider}")
                self.service = GeminiService() # Default fallback

    def generate_product_description(self, product_name, raw_data_str):
        prompt = f"""
        Siz professional kopiraytersiz. Quyidagi mahsulot haqidagi ma'lumotlarni o'rganib chiqing va uni chiroyli, 
        sotiladigan (professional) va JUDA BATAFSIL ko'rinishga keltiring.
        
        Mahsulot nomi: {product_name}
        Xom ma'lumotlar: {raw_data_str}
        
        Talablar:
        1. HTML formatida bo'lsin (p, ul, li, strong, h3 teglaridan foydalaning).
        2. O'zbek tilida bo'lsin.
        3. Mahsulotning afzalliklari va foydalanish sohalarini batafsil yozing.
        4. Tavsif qismi ishonchli va sotiladigan bo'lsin.
        5. Faqat HTML kodini qaytaring.
        """
        if self.provider == 'puter':
            return self.service.generate_sync(prompt, model=self.model_id)
        return self.service.generate_product_description(product_name, raw_data_str)

    def parse_product_specs(self, product_name, raw_data_str):
        prompt = f"""
        Quyidagi xom ma'lumotlardan mahsulot xususiyatlarini MAKSIMAL darajada ajratib oling va JSON formatida qaytaring.
        
        Mahsulot nomi: {product_name}
        Xom ma'lumotlar: {raw_data_str}
        
        JSON keys: brand, manufacturer, model, series, color, material, weight, dimensions, category, 
                   subcategory, country, country_code, sku, article_code, barcode, warranty_period, rating, 
                   seo_keywords, popularity_score.
        Agar ma'lumot topilmasa, null qo'ying.
        Faqat JSON qaytaring.
        """
        if self.provider == 'puter':
            import json
            try:
                res = self.service.generate_sync(prompt, model=self.model_id)
                clean_text = res.replace('```json', '').replace('```', '').strip()
                return json.loads(clean_text)
            except:
                return {}
        return self.service.parse_product_specs(product_name, raw_data_str)

    def generate_with_search(self, product_name):
        return self.service.generate_with_search(product_name)

    def generate_with_knowledge(self, product_name):
        return self.service.generate_with_knowledge(product_name)

    def generate_image(self, prompt):
        """
        Generates an image based on the prompt.
        Currently primarily supported by Puter.
        """
        if self.provider == 'puter':
            return self.service.generate_image_sync(prompt)
        # Add fallback or other providers later
        return None
