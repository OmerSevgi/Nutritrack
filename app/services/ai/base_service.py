import os
import json
from groq import Groq
import google.generativeai as genai
from flask import current_app

class AIBaseService:
    def __init__(self):
        self.groq_key = current_app.config.get('GROQ_API_KEY')
        self.gemini_key = current_app.config.get('GEMINI_API_KEY')
        
        if self.groq_key:
            self.groq_client = Groq(api_key=self.groq_key)
            self.groq_model = "llama-3.3-70b-versatile"
            
        if self.gemini_key:
            genai.configure(api_key=self.gemini_key)
            self.gemini_model = genai.GenerativeModel('gemini-2.0-flash-lite')

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

    def _call_gemini(self, prompt):
        try:
            response = self.gemini_model.generate_content(prompt)
            return response.text.strip().replace("```json", "").replace("```", "")
        except Exception as e:
            print(f"Gemini Error: {e}")
            return None
