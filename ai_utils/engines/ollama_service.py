import ollama
import requests

class OllamaService():
    def __init__(self,
                 model: str = "qwen2.5:14b-instruct"
                 ):
        self.engine = ollama
        self.model = model

    def _is_available(self) -> bool:
        """
        Check if Ollama service is available at localhost:11434
        """
        try:
            response = requests.get('http://localhost:11434')
            if response.status_code == 200:
                return True
            else:
                return False
        except requests.exceptions.ConnectionError:
            return False

    def chat(self, message, system_prompt) -> str:
        """ 
        Respond to a message generically
        """
        if not self._is_available():
            return "Unfortunately my brain is not available right now. Please try again later."

        response = self.engine.chat(model=self.model, messages=[
            {
                'role': 'system',
                'content': system_prompt,
            },
            {
                'role': 'user',
                'content': f"{message}",
            },
        ])

        return response['message']['content']

    def chat_with_files(self, message, system_prompt, files) -> str:
        return "Unfortunately I can't see images yet. Please try again later."