from ai_utils.engines.ollama_service import OllamaService
from ai_utils.engines.gemini_service import GeminiService
from utils.config import LLM_ENGINE, LLM_MODEL
from ai_utils.llm_utils import SYS_PROMPT_WITH_CONTEXT

class LLMService():
    def __init__(self,
                 engine: str = LLM_ENGINE,
                 model: str = LLM_MODEL,
                 system_prompt: str = SYS_PROMPT_WITH_CONTEXT
                 ):
        self.model = model
        self.engine = self._get_engine(engine)
        self.system_prompt = system_prompt

    def _get_engine(self, engine: str):
        """
        Select the engine to use
        """
        if engine == "ollama":
            return OllamaService(model=self.model)
        elif engine == "gemini":
            return GeminiService(model=self.model)
        else:
            raise ValueError("Engine not found")
        
    def set_sys_prompt(self, system_prompt: str):
        """
        Set the system prompt
        """
        self.system_prompt = system_prompt
        
    def is_available(self) -> bool:
        """
        Check if selected service is available
        """
        return self.engine._is_available()
    
    def chat(self, message, system_prompt = None, files=None) -> str:
        """ 
        Respond to a message generically
        """
        if system_prompt is None:
            system_prompt = self.system_prompt

        if files is None:
            return self.engine.chat(message, system_prompt)
        else:
            return self.engine.chat_with_files(message, system_prompt, files)
    
class BlankLLMService():
    def __init__(self):
        pass
    
    def is_available(self) -> bool:
        return False
    
    def chat(self, message, system_prompt) -> str:
        return "My brain is not enabled right now. Please try again later."