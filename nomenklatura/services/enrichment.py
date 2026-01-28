import requests
import logging
from django.conf import settings
from django.core.files.base import ContentFile
from django.utils import timezone
from nomenklatura.models import Nomenklatura, NomenklaturaImage
from utils.ai.gemini import GeminiService
from utils.settings import get_system_setting
import os

logger = logging.getLogger(__name__)

class NomenklaturaEnrichmentService:
    def __init__(self):
        self.gemini = GeminiService()
        self.search_api_key = get_system_setting('SEARCH_API_KEY')
        self.serper_url = "https://google.serper.dev/search"

    def search_product(self, query):
        """
        Searches for product info using Serper.dev API
        """
        if not self.search_api_key:
            logger.error("SEARCH_API_KEY not found")
            return None, []

        headers = {
            'X-API-KEY': self.search_api_key,
            'Content-Type': 'application/json'
        }
        payload = {
            'q': query,
            'gl': 'uz', # Uzbekistan region
            'hl': 'uz'  # Uzbek language
        }

        try:
            response = requests.post(self.serper_url, headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()
            
            # Extract snippets for Gemini
            snippets = []
            if 'organic' in data:
                for item in data['organic']:
                    snippets.append(f"Title: {item.get('title')}\nSnippet: {item.get('snippet')}")
            
            # Extract image URLs if available (Serper 'images' endpoint is separate, but organic might have some or we can do a second call)
            # For now, let's just focus on organic for text and maybe add image search later or use a dedicated image search
            return "\n\n".join(snippets), []
        except Exception as e:
            logger.error(f"Search error: {str(e)}")
            return None, []

    def search_images(self, query):
        """
        Searches for product images using Serper.dev Images API
        """
        if not self.search_api_key:
            return []

        headers = {'X-API-KEY': self.search_api_key, 'Content-Type': 'application/json'}
        payload = {'q': query}
        url = "https://google.serper.dev/images"

        try:
            response = requests.post(url, headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()
            return [img.get('imageUrl') for img in data.get('images', [])[:5]] # Get top 5
        except Exception as e:
            logger.error(f"Image search error: {str(e)}")
            return []

    def enrich_instance(self, nomenklatura):
        """
        Main logic to enrich a Nomenklatura instance
        """
        nomenklatura.enrichment_status = 'IN_PROGRESS'
        nomenklatura.save()

        query = f"{nomenklatura.name} {nomenklatura.article_code or ''} {nomenklatura.brand or ''} {nomenklatura.category or ''} {nomenklatura.roditel or ''}".strip()
        logger.info(f"Enriching product with query: {query}")

        description = ""
        specs = {}

        # 1. Try Serper Search (Best for real-time/niche data)
        if self.search_api_key:
            try:
                raw_text, _ = self.search_product(query)
                if raw_text:
                    description = self.gemini.generate_product_description(nomenklatura.name, raw_text)
                    specs = self.gemini.parse_product_specs(nomenklatura.name, raw_text)
            except Exception as e:
                logger.error(f"Serper enrichment failed: {e}")

        # 2. Try Gemini Search Grounding (Free fallback)
        if not description and not specs:
            logger.info("Using Gemini Search Grounding fallback")
            grounded_res = self.gemini.generate_with_search(query)
            if grounded_res:
                description, specs = self._parse_grounded_response(grounded_res)

        # 3. Try Gemini Internal Knowledge (Final fallback)
        if not description and not specs:
            logger.info("Using Gemini Internal Knowledge fallback")
            knowledge_res = self.gemini.generate_with_knowledge(query)
            if knowledge_res:
                description, specs = self._parse_grounded_response(knowledge_res)

        if not description and not specs:
            nomenklatura.enrichment_status = 'FAILED'
            nomenklatura.save()
            return False

        if description:
            nomenklatura.description = description
        
        if specs:
            # Update fields if Gemini found them and they are empty
            fields_to_update = [
                'brand', 'manufacturer', 'model', 'series', 'color', 'material', 
                'weight', 'dimensions', 'category', 'subcategory', 'country', 
                'country_code', 'sku', 'article_code', 'barcode', 'warranty_period', 
                'rating', 'seo_keywords', 'popularity_score'
            ]
            for field in fields_to_update:
                val = specs.get(field)
                if val and not getattr(nomenklatura, field):
                    setattr(nomenklatura, field, val)

        # 4. Search and download images if no images exist (Only if search key present)
        if not nomenklatura.images.exists() and self.search_api_key:
            image_urls = self.search_images(query)
            for i, url in enumerate(image_urls):
                try:
                    img_data = requests.get(url, timeout=10).content
                    img_name = f"{nomenklatura.code_1c}_{i}.jpg"
                    
                    ni = NomenklaturaImage(
                        nomenklatura=nomenklatura,
                        is_main=(i == 0),
                        note=f"AI Generated from {url[:50]}...",
                        is_ai_generated=True
                    )
                    ni.image.save(img_name, ContentFile(img_data), save=True)
                except Exception as e:
                    logger.error(f"Failed to download image {url}: {str(e)}")

        nomenklatura.enrichment_status = 'COMPLETED'
        nomenklatura.last_enriched_at = timezone.now()
        nomenklatura.save()
        return True

    def _parse_grounded_response(self, text):
        """Helper to parse the grounded response from Gemini"""
        description = ""
        specs = {}
        
        try:
            if "---DESCRIPTION---" in text and "---SPECS---" in text:
                parts = text.split("---SPECS---")
                desc_part = parts[0].replace("---DESCRIPTION---", "").strip()
                specs_part = parts[1].strip()
                
                description = desc_part
                
                # Clean JSON
                clean_json = specs_part.replace('```json', '').replace('```', '').strip()
                import json
                specs = json.loads(clean_json)
            else:
                description = text # Fallback
        except Exception as e:
            logger.error(f"Error parsing grounded response: {e}")
            
        return description, specs


    def clear_enrichment(self, nomenklatura):
        """
        Clears AI-enriched data and deletes AI-generated images
        """
        # 1. Clear text fields (descriptions and specific tags if enriched)
        # We only clear description if it was changed by AI. 
        # For simplicity, we clear it if status is COMPLETED or FAILED
        nomenklatura.description = ""
        
        # 2. Delete AI generated images
        ai_images = nomenklatura.images.filter(is_ai_generated=True)
        for img in ai_images:
            img.image.delete(save=False)
            img.delete()
            
        # 3. Reset status
        nomenklatura.enrichment_status = 'PENDING'
        nomenklatura.last_enriched_at = None
        nomenklatura.save()
        return True
