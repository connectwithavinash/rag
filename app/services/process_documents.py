from google.genai import types
from ..prompts.prompts_manager import PromptManager
from ..providers.llm.gemini import GeminiClient
import pymupdf
from ..core.logging import get_logger
from ..core.config import get_settings
import asyncio
from concurrent.futures import ThreadPoolExecutor

logger = get_logger()

# Create a global ThreadPoolExecutor for blocking operations
# Adjust max_workers based on your system's core count and expected load
executor = ThreadPoolExecutor(max_workers=4) 

async def extract_details(
        collection_name :str,
        document,
        prompt_manager : PromptManager, 
        client : GeminiClient
        ):  
        settings = get_settings()
        semaphore = asyncio.Semaphore(settings.gemini_rate_limit)

        async def _process_page(page_pdf_bytes: bytes, prompt_content):
            async with semaphore:
                content = [types.Part.from_bytes(
                    data=page_pdf_bytes,
                    mime_type='application/pdf',
                ),
                prompt_content]
                response = await client.generate_response(content)
                return response.text

        try:
            prompt = prompt_manager.get_prompt(collection_name)
            
            # Offload pymupdf operations to the thread pool
            loop = asyncio.get_running_loop()
            doc = await loop.run_in_executor(executor, lambda: pymupdf.open(stream=document, filetype="pdf"))
            
            tasks = []
            for page_index in range(doc.page_count):
                # Offload page extraction to the thread pool
                page_pdf_bytes = await loop.run_in_executor(executor, lambda idx=page_index: _get_page_bytes(doc, idx))
                tasks.append(_process_page(page_pdf_bytes, prompt))
            
            responses = await asyncio.gather(*tasks)
            all_responses = "".join([res for res in responses if isinstance(res, str)])
            
            return all_responses
                
        except Exception as e:
             logger.error(f"Exception Occured: {e}", exc_info=True)

def _get_page_bytes(doc, page_index):
    single_page_doc = pymupdf.open()  
    single_page_doc.insert_pdf(doc, from_page=page_index, to_page=page_index)
    pdf_bytes = single_page_doc.write()
    single_page_doc.close()  
    return pdf_bytes