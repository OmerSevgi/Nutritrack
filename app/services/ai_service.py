import os
import json
import google.generativeai as genai
from flask import current_app

class AIService:
    def __init__(self):
        try:
            api_key = current_app.config.get('GEMINI_API_KEY')
            if not api_key:
                print("DEBUG: [AIService] GEMINI_API_KEY is None!")
            
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel('gemini-2.0-flash')
        except Exception as e:
            print(f"DEBUG: [AIService] Failed to initialize Gemini: {str(e)}")

    def generate_response(self, user_profile, daily_status, user_query):
        try:
            prompt = f"""
            Sen bir profesyonel beslenme ve spor koçusun. 
            Kullanıcı Bilgileri: Yaş: {user_profile['age']}, Boy: {user_profile['height']}, Kilo: {user_profile['weight']}, Hedef: {user_profile['goal']}.
            Bugünkü Durum: Kalori: {daily_status['calories']}/{user_profile['target_calories']}, Protein: {daily_status['protein']}g/{user_profile['target_protein']}g.
            
            Kullanıcı sorusu: {user_query}
            Lütfen kısa, bilimsel ve motive edici cevap ver.
            """
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"AI servisi şu an yanıt veremiyor: {str(e)}"

    def parse_food_input(self, text):
        try:
            system_prompt = """
            Görevin kullanıcı girdilerini analiz etmek ve kalori ile makro değerlerini hesaplamaktır.
            Sadece JSON döndür. 
            Format:
            {
              "besinler": [
                {
                  "ad": "Besin Adı",
                  "miktar": "100g",
                  "kalori": 0,
                  "protein": 0,
                  "karbonhidrat": 0,
                  "yag": 0
                }
              ]
            }
            """
            prompt = f"{system_prompt}\nÖğün Metni: {text}"
            response = self.model.generate_content(prompt)
            
            # Markdown temizliği
            raw_text = response.text.strip().replace("```json", "").replace("```", "")
            
            data = json.loads(raw_text)
            return data.get("besinler", [])
        except Exception as e:
            # Debug: Liste modelleri ve hatayı yazdır
            print(f"Error parsing food input: {str(e)}")
            try:
                for m in genai.list_models():
                    if 'generateContent' in m.supported_generation_methods:
                        print(f"Supported model: {m.name}")
            except Exception as inner_e:
                print(f"Could not list models: {inner_e}")
            return []

    def ask_coach(self, query):
        try:
            response = self.model.generate_content(query)
            return response.text
        except Exception as e:
            return f"Hata: {str(e)}"

    def generate_fridge_recipe(self, user_profile, ingredients):
        try:
            prompt = f"Hedef: {user_profile['goal']}. Malzemeler: {ingredients}. Sağlıklı bir tarif üret ve makro değerlerini ekle."
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"Tarif oluşturulamadı: {str(e)}"
