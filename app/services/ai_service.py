import os
import json
from groq import Groq
from flask import current_app
from functools import lru_cache
from app.integrations.spoonacular_client import SpoonacularClient
from app.integrations.ninjas_client import ExerciseClient

class AIService:
    def __init__(self):
        try:
            self.client = Groq(api_key=current_app.config.get('GROQ_API_KEY'))
            self.model = "llama-3.3-70b-versatile"
            self.spoonacular = SpoonacularClient()
            self.exercise_client = ExerciseClient()
        except Exception as e:
            print(f"DEBUG: [AIService] Groq initialization error: {str(e)}")

    @lru_cache(maxsize=32)
    def get_exercises_from_api(self, muscle):
        return self.exercise_client.get_exercises(muscle=muscle)

    def orchestrate_fitness_plan(self, user_profile, muscle):
        exercises = self.get_exercises_from_api(muscle)
        if not exercises: return "Bu kas grubu için egzersiz bulunamadı."
        
        prompt = f"""
        Kullanıcı hedefi: {user_profile['goal']}.
        Bu kas grubu için antrenman önerisi: {json.dumps(exercises[:5])}
        Kullanıcıya bu egzersizleri hedefine göre nasıl yapması gerektiğini profesyonelce açıkla.
        """
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content

    def get_recipe_suggestions(self, ingredients):
        recipes = self.spoonacular.find_recipes(ingredients)
        if not recipes: return "Malzemelerinle uygun tarif bulamadım."
        
        prompt = f"Bulunan tarifler: {json.dumps(recipes)}. Bunları kullanıcının hedefine uygun şekilde seç ve kısa tariflerini ver."
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content

    def parse_food_input(self, text):
        try:
            system_prompt = """
            Sen uzman bir diyetisyen ve veri mühendisisin. Görevin, kullanıcıdan gelen besin girdilerini bilimsel besin veritabanı değerlerine göre analiz etmektir.
            Sadece geçerli bir JSON döndür.
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
            """
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Öğün Metni: {text}"}
                ],
                response_format={"type": "json_object"},
                temperature=0.1
            )
            data = json.loads(completion.choices[0].message.content)
            return data.get("besinler", [])
        except Exception as e:
            print(f"Error parsing food input: {str(e)}")
            return []

    def ask_coach(self, query):
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": query}]
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Hata: {str(e)}"

    def generate_fridge_recipe(self, user_profile, ingredients):
        try:
            prompt = f"Hedef: {user_profile['goal']}. Malzemeler: {ingredients}. Sağlıklı bir tarif üret ve makro değerlerini ekle."
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}]
            )
            return response.choices[0].message.content
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
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"}
            )
            return json.loads(completion.choices[0].message.content)
        except Exception as e:
            print(f"Error analyzing workout: {str(e)}")
            return None

    def generate_weekly_fitness_report(self, user_profile, weekly_stats):
        try:
            stats_context = "\n".join([f"- {ex}: Toplam Hacim {d['total_volume']}kg, Max {d['max_weight']}kg" for ex, d in weekly_stats.items()])
            prompt = f"Sen Baş Antrenörsün. {user_profile['goal']} hedefine göre haftalık özetle: {stats_context}"
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}]
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Rapor oluşturulamadı: {str(e)}"
