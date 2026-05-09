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
            self.model = genai.GenerativeModel('gemini-2.5-flash-lite')
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
            Sen uzman bir diyetisyen ve veri mühendisisin. Görevin, kullanıcıdan gelen besin girdilerini bilimsel besin veritabanı (USDA standartları) değerlerine göre analiz etmektir.

            KURALLAR (KESİNLİKLE UY):
            1. BİRİM HESABI: 100g bazlı değerleri kullan. 'kalori', 'protein', 'karbonhidrat', 'yag' değerleri 100g içindir.
            2. TOPLAM HESABI: Kullanıcının girdiği miktara (örn: 200g) göre 'toplam_kalori' vb. değerleri (Birim Değer * Miktar / 100) formülüyle hesapla.
            3. HESAPLAMA MANTIĞI: 
               - 1 yumurta (orta boy) ~75 kcal | 6g Protein | 0.5g Karb | 5g Yağ
               - 100g Tavuk Göğsü (pişmiş) ~165 kcal | 31g Protein | 0g Karb | 3.6g Yağ
               - 100g Beyaz Pirinç (pişmiş) ~130 kcal | 2.7g Protein | 28g Karb | 0.3g Yağ
            4. HATA PAYI: Eğer besin tam eşleşmiyorsa en yakın standart değeri kullan, asla uydurma.

            ÇIKTI FORMATI (Sadece JSON):
            {
              "besinler": [
                {
                  "ad": "Besin Adı",
                  "miktar": "150g",
                  "kalori": 165,
                  "protein": 31,
                  "karbonhidrat": 0,
                  "yag": 3.6
                }
              ]
            }
            * Not: Döndürdüğün değerler 100g (birim) bazlı değil, kullanıcının yediği toplam miktara göre hesaplanmış (total) değerler olsun.
            """
            prompt = f"{system_prompt}\nÖğün Metni: {text}"
            
            # Hız ve doğruluk optimizasyonu (Sadece bu metod için)
            generation_config = {
                "temperature": 0.0,
                "max_output_tokens": 400
            }
            
            response = self.model.generate_content(prompt, generation_config=generation_config)
            
            # Markdown temizliği
            raw_text = response.text.strip().replace("```json", "").replace("```", "")
            
            data = json.loads(raw_text)
            return data.get("besinler", [])
        except Exception as e:
            print(f"Error parsing food input: {str(e)}")
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

    def analyze_workout(self, user_profile, workout_text, workout_history=None):
        try:
            history_context = "Son antrenmanların:\n" + "\n".join([f"- {h['date']}: {h['description']}" for h in workout_history]) if workout_history else ""
            prompt = f"""
            Sen NutriTrack uygulamasının kıdemli Personal Trainer'ısın. 
            GÖREVİN: Kullanıcının antrenmanını analiz et ve JSON döndür.
            
            JSON FORMATI DÖN:
            {{
                "exercises": [{{"name": "Bench Press", "weight": 60, "sets": 3, "reps": 10}}],
                "feedback": "..."
            }}
            
            Bugünkü antrenman: {workout_text}
            """
            response = self.model.generate_content(prompt)
            return json.loads(response.text.strip().replace("```json", "").replace("```", ""))
        except Exception as e:
            print(f"Error analyzing workout: {str(e)}")
            return None

    def generate_weekly_fitness_report(self, user_profile, weekly_stats):
        try:
            stats_context = "\n".join([f"- {ex}: Toplam Hacim {d['total_volume']}kg, Max {d['max_weight']}kg" for ex, d in weekly_stats.items()])
            prompt = f"Sen Baş Antrenörsün. {user_profile['goal']} hedefine göre haftalık özetle: {stats_context}"
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"Rapor oluşturulamadı: {str(e)}"
