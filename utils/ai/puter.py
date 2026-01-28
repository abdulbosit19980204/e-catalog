import logging
import asyncio
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

    async def generate_content(self, prompt, model="gpt-4o"):
        """
        Generates content using Puter's AI
        """
        await self._ensure_login()
        try:
            # Based on dir(PuterClient), the method is ai_chat
            response = await self.client.ai_chat(prompt, model=model)
            # Response might be an object with message or just a string
            if hasattr(response, 'message'):
                return response.message
            return str(response)
        except Exception as e:
            logger.error(f"Puter generation error: {e}")
            raise Exception(f"Puter ({model}) xatoligi: {str(e)}")

    def generate_sync(self, prompt, model="gpt-4o"):
        """Sync wrapper for async generate_content"""
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # If we are in a running loop (like Django async?), this is tricky.
                # But typically Django runserver/worker is sync context.
                return asyncio.run_coroutine_threadsafe(self.generate_content(prompt, model), loop).result()
            return loop.run_until_complete(self.generate_content(prompt, model))
        except RuntimeError:
            return asyncio.run(self.generate_content(prompt, model))

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
        # Puter doesn't have native grounding/search in the same way as Gemini yet
        # but we can just use prompt
        return self.generate_sync(f"Search web for {query} and summarize details.")

    def generate_with_knowledge(self, query):
        return self.generate_sync(query)
