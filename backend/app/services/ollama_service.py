import ollama
from app.config import settings

GPU_MODELS = {
    "llama3.2:1b": "llama3.2:3b",
    "llama3.2:3b": "llama3.2:3b",
    "llama3.1:8b": "llama3.1:8b",
}

CPU_MODEL = "llama3.2:1b"


class OllamaService:
    def __init__(self):
        self.base_model = settings.OLLAMA_MODEL
        self.client = ollama.Client(host=settings.OLLAMA_BASE_URL)
        self.model = self._select_model()

    def _select_model(self) -> str:
        """Auto-detect GPU and select appropriate model"""
        try:
            info = self.client.show(self.base_model)
            if "gpu" in info.get("model_info", {}):
                return GPU_MODELS.get(self.base_model, self.base_model)
        except:
            pass
        return CPU_MODEL

    def _has_gpu(self) -> bool:
        """Check if GPU is available"""
        try:
            info = self.client.show(self.base_model)
            return "gpu" in str(info).lower()
        except:
            return False

    async def generate(self, prompt: str, system_prompt: str = None) -> str:
        """Generate response from Ollama"""
        messages = []

        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})

        messages.append({"role": "user", "content": prompt})

        try:
            response = self.client.chat(model=self.model, messages=messages)
            return response["message"]["content"]
        except Exception as e:
            raise Exception(f"Ollama generation failed: {str(e)}")

    def test_connection(self) -> bool:
        """Test if Ollama is running"""
        try:
            self.client.list()
            return True
        except:
            return False
