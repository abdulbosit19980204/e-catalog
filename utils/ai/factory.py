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
        if self.provider == 'puter':
            prompt = f"Product: {product_name}\nData: {raw_data_str}\nGenerate a professional detailed HTML description in Uzbek."
            return self.service.generate_sync(prompt, model=self.model_id)
        return self.service.generate_product_description(product_name, raw_data_str)

    def parse_product_specs(self, product_name, raw_data_str):
        if self.provider == 'puter':
            prompt = f"Product: {product_name}\nData: {raw_data_str}\nParse into JSON with keys: brand, manufacturer, model, color, material, weight, dimensions, category. Return ONLY JSON."
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
