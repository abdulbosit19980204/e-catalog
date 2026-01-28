import google.generativeai as genai
import os
import json
import logging
from django.conf import settings
from utils.settings import get_system_setting

logger = logging.getLogger(__name__)

class GeminiService:
    def __init__(self):
        from core.models import AIModel
        api_key = get_system_setting('GEMINI_API_KEY')
        
        # Fetch active models from database
        active_models = AIModel.objects.filter(is_active=True)
        self.model_names = [m.model_id for m in active_models]
        
        # Primary model is the one marked is_default, or the first active one
        primary_model = active_models.filter(is_default=True).first() or active_models.first()
        self.primary_model_name = primary_model.model_id if primary_model else 'models/gemini-2.5-flash'
        
        if not api_key:
            logger.error("GEMINI_API_KEY not found")
            raise ValueError("GEMINI_API_KEY is required")
        
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(self.primary_model_name)
        
        # Free fallback using Google Search grounding
        # Try new 'google_search' tool first, then fallback to 'google_search_retrieval'
        try:
            self.model_with_search = genai.GenerativeModel(
                model_name=self.primary_model_name,
                tools=[{"google_search": {}}]
            )
        except Exception as e:
            logger.warning(f"Could not initialize 'google_search' tool, trying 'google_search_retrieval': {e}")
            try:
                self.model_with_search = genai.GenerativeModel(
                    model_name=self.primary_model_name,
                    tools=[{"google_search_retrieval": {}}]
                )
            except Exception as e2:
                logger.error(f"Failed to initialize any search tool: {e2}")
                self.model_with_search = self.model

    def _log_usage(self, response, purpose):
        """Helper to log token usage to the database"""
        try:
            from core.models import AITokenUsage
            usage = response.usage_metadata
            AITokenUsage.objects.create(
                model_name=self.model.model_name,
                input_tokens=usage.prompt_token_count,
                output_tokens=usage.candidates_token_count,
                total_tokens=usage.total_token_count,
                purpose=purpose
            )
        except Exception as e:
            logger.error(f"Error logging token usage: {e}")

    def generate_product_description(self, product_name, raw_data_str):
        """
        Generates a professional product description in HTML/RichText format
        """
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
        
        try:
            response = self.model.generate_content(prompt)
            self._log_usage(response, f"Description: {product_name}")
            return response.text
        except Exception as e:
            logger.error(f"Error generating content with Gemini: {str(e)}")
            return None

    def parse_product_specs(self, product_name, raw_data_str):
        """
        Parses raw data into a structured JSON for model fields
        """
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
        
        try:
            response = self.model.generate_content(prompt)
            self._log_usage(response, f"Specs: {product_name}")
            # Remove markdown code blocks if present
            clean_text = response.text.replace('```json', '').replace('```', '').strip()
            return json.loads(clean_text)
        except Exception as e:
            logger.error(f"Error parsing specs with Gemini: {str(e)}")
            return {}

    def generate_with_search(self, product_name):
        """
        Uses Google Search grounding to find info and generate description/specs.
        Useful when SEARCH_API_KEY is missing.
        """
        prompt = f"""
        Internetdan quyidagi mahsulot haqida BARCHA texnik ma'lumotlarni qidiring: {product_name}
        
        Sizdan 2 ta narsa talab qilinadi:
        1. Mahsulot Tavsifi (Batafsil HTML formatida, o'zbek tilida).
        2. Mahsulot Xususiyatlari (To'liq JSON formatida).
        
        JSON keys: brand, manufacturer, model, series, color, material, weight, dimensions, category, 
                   subcategory, country, country_code, sku, article_code, barcode, warranty_period, rating, 
                   seo_keywords, popularity_score.
        
        Muhim: MAKSIMAL darajada to'ldiring.
        Javobni quyidagi formatda qaytaring:
        ---DESCRIPTION---
        [HTML tavsif]
        ---SPECS---
        [JSON xususiyatlar]
        """
        
        try:
            response = self.model_with_search.generate_content(prompt)
            self._log_usage(response, f"Search grounding: {product_name}")
            return response.text
        except Exception as e:
            logger.error(f"Error generating content with search grounding: {str(e)}")
            return self.generate_with_knowledge(product_name)

    def generate_with_knowledge(self, product_name):
        """
        Fallback to internal knowledge when search grounding fails.
        """
        prompt = f"""
        O'z bilimingizga tayanib, quyidagi mahsulot haqida ma'lumot bering: {product_name}
        
        1. Mahsulot Tavsifi (Batafsil HTML formatida, o'zbek tilida).
        2. Mahsulot Xususiyatlari (To'liq JSON formatida).
        
        JSON keys: brand, manufacturer, model, series, color, material, weight, dimensions, category, 
                   subcategory, country, country_code, sku, article_code, barcode, warranty_period, rating, 
                   seo_keywords, popularity_score.
        
        Javobni quyidagi formatda qaytaring:
        ---DESCRIPTION---
        [HTML tavsif]
        ---SPECS---
        [JSON xususiyatlar]
        """
        try:
            response = self.model.generate_content(prompt)
            self._log_usage(response, f"Internal Knowledge: {product_name}")
            return response.text
        except Exception as e:
            logger.error(f"Error generating content with knowledge: {str(e)}")
            return None
