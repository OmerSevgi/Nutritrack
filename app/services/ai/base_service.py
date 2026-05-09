import os
import json
from groq import Groq
from flask import current_app

class AIBaseService:
    def __init__(self):
        self.groq_key = current_app.config.get('GROQ_API_KEY')
        
        if self.groq_key:
            self.groq_client = Groq(api_key=self.groq_key)
            self.groq_model = "llama-3.3-70b-versatile"
        else:
            print("CRITICAL: GROQ_API_KEY is not set!")

    def _call_groq(self, prompt, json_mode=False):
        try:
            params = {
                "model": self.groq_model,
                "messages": [{"role": "user", "content": prompt}]
            }
            if json_mode:
                params["response_format"] = {"type": "json_object"}
            
            response = self.groq_client.chat.completions.create(**params)
            return response.choices[0].message.content
        except Exception as e:
            print(f"Groq Error: {e}")
            return None
