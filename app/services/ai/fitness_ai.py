import json
from app.services.ai.base_service import AIBaseService
from app.integrations.ninjas_client import ExerciseClient

class FitnessAIService(AIBaseService):
    def __init__(self):
        super().__init__()
        self.exercise_client = ExerciseClient()

    def analyze_workout(self, user_profile, workout_text, workout_history=None):
        program_context = f"\nKullanıcın Sabit Fitness Programı:\n{user_profile.get('fitness_program', 'Belirtilmemiş')}\n"
        
        prompt = f"""
        Sen profesyonel bir fitness antrenörüsün. Kullanıcının girdiği antrenman metnini analiz et.
        {program_context}
        Eğer kullanıcı sabit programına sadık kalmışsa veya dışına çıkmışsa bunu feedback kısmında belirt.
        
        Sadece şu JSON formatında döndür:
        {{
            "exercises": [
                {{"name": "Egzersiz Adı", "weight": ağırlık_kg, "sets": set_sayısı, "reps": tekrar_sayısı}}
            ],
            "feedback": "Antrenman hakkındaki profesyonel yorumun"
        }}
        
        Metin: {workout_text}
        """
        raw_json = self._call_groq(prompt, json_mode=True)
        try:
            return json.loads(raw_json)
        except:
            return None

    def orchestrate_fitness_plan(self, user_goal, muscle):
        exercises = self.exercise_client.get_exercises(muscle=muscle)
        if not exercises: return "Egzersiz bulunamadı."
        prompt = f"Hedef: {user_goal}. Egzersizler: {json.dumps(exercises[:5])}. Profesyonelce açıkla."
        return self._call_groq(prompt)
