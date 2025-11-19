import ollama
from app.config import settings

class OllamaService:
    def __init__(self):
        self.model = settings.OLLAMA_MODEL
        self.client = ollama.Client(host=settings.OLLAMA_BASE_URL)
    
    async def generate(self, prompt: str, system_prompt: str = None) -> str:
        """Generate response from Ollama"""
        messages = []
        
        if system_prompt:
            messages.append({
                "role": "system",
                "content": system_prompt
            })
        
        messages.append({
            "role": "user",
            "content": prompt
        })
        
        try:
            response = self.client.chat(
                model=self.model,
                messages=messages
            )
            return response['message']['content']
        except Exception as e:
            raise Exception(f"Ollama generation failed: {str(e)}")
    
    def test_connection(self) -> bool:
        """Test if Ollama is running"""
        try:
            self.client.list()
            return True
        except:
            return False
