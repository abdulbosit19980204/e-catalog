import logging
import asyncio
from asgiref.sync import async_to_sync
from putergenai import PuterClient
from utils.settings import get_system_setting

logger = logging.getLogger(__name__)

class PuterService:
    def __init__(self):
        self.username = get_system_setting('PUTER_USERNAME')
        self.password = get_system_setting('PUTER_PASSWORD')
        self.client = PuterClient()
        self.is_logged_in = False

    async def _ensure_login(self):
        if not self.is_logged_in:
            if not self.username or not self.password:
                logger.error("PUTER_USERNAME or PUTER_PASSWORD not found")
                raise ValueError("Puter credentials required (Admin -> Settings -> Sozlamalar)")
            
            try:
                await self.client.login(self.username, self.password)
                self.is_logged_in = True
            except Exception as e:
                logger.error(f"Puter login failed: {e}")
                raise Exception(f"Puter login xatoligi: {str(e)}")

    async def _generate_content_async(self, prompt, model="gpt-4o"):
        await self._ensure_login()
        try:
            response = await self.client.ai_chat(prompt, model=model)
            if hasattr(response, 'message'):
                return response.message
            return str(response)
        except Exception as e:
            logger.error(f"Puter generation error: {e}")
            raise Exception(f"Puter ({model}) xatoligi: {str(e)}")

    async def _generate_image_async(self, prompt, model="gpt-image-1.5"):
        await self._ensure_login()
        try:
            # ai_txt2img might return bytes or an object with bytes/link
            response = await self.client.ai_txt2img(prompt, model=model)
            if isinstance(response, bytes):
                return response
            if hasattr(response, 'data'):
                return response.data
            if hasattr(response, 'bytes'):
                return response.bytes
            return response
        except Exception as e:
            logger.error(f"Puter image generation error: {e}")
            raise Exception(f"Puter Image ({model}) xatoligi: {str(e)}")

    def generate_sync(self, prompt, model="gpt-4o"):
        return async_to_sync(self._generate_content_async)(prompt, model)

    def generate_image_sync(self, prompt, model="gpt-image-1.5"):
        return async_to_sync(self._generate_image_async)(prompt, model)

    def generate_product_description(self, product_name, raw_data_str):
        prompt = f"Product: {product_name}\nData: {raw_data_str}\nGenerate a professional detailed HTML description in Uzbek."
        return self.generate_sync(prompt)

    def parse_product_specs(self, product_name, raw_data_str):
        prompt = f"Product: {product_name}\nData: {raw_data_str}\nParse into JSON with specific technical fields. Return ONLY JSON."
        import json
        try:
            res = self.generate_sync(prompt)
            clean_text = res.replace('```json', '').replace('```', '').strip()
            return json.loads(clean_text)
        except:
            return {}

    def generate_with_search(self, query):
        return self.generate_sync(f"Search web for {query} and summarize details.")

    def generate_with_knowledge(self, query):
        return self.generate_sync(query)
