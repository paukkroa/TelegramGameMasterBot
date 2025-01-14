import google.generativeai as genai
import os

class GeminiService():
    def __init__(self,
                 model: str = "gemini-2.0-flash-exp"
                 ):
        self.engine = genai
        self.model = model

    def _is_available(self) -> bool:
        """
        Check if Gemini service is available
        """
        try:
            genai.configure(api_key=os.environ["GOOGLE_API_KEY"])
            return True
        except:
            return False

    def chat(self, message, system_prompt) -> str:
        """ 
        Respond to a message generically
        """
        if not self._is_available():
            return "Unfortunately my brain is not available right now. Please try again later."
        
        generation_config = {
            "temperature": 1.45,
            "top_p": 0.9,
            "top_k": 40,
            "max_output_tokens": 8192,
            "response_mime_type": "text/plain",
        }

        model = genai.GenerativeModel(self.model,
                                      generation_config=generation_config,
                                      system_instruction=[system_prompt])
        response = model.generate_content(message)
        return response.candidates[0].content.parts[0].text
