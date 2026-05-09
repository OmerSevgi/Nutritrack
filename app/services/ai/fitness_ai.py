import json
from app.services.ai.base_service import AIBaseService
from app.integrations.ninjas_client import ExerciseClient

class FitnessAIService(AIBaseService):
    def __init__(self):
        super().__init__()
        self.exercise_client = ExerciseClient()

    def analyze_workout(self, user_profile, workout_text, history=None):
        prompt = f"""
        Antrenmanı analiz et ve JSON döndür:
        {{"exercises": [{{"name": "Bench Press", "weight": 60, "sets": 3, "reps": 10}}], "feedback": "..."}}
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
