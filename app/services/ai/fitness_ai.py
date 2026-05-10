import json
from app.services.ai.base_service import AIBaseService
from app.integrations.ninjas_client import ExerciseClient

class FitnessAIService(AIBaseService):
    def __init__(self):
        super().__init__()
        self.exercise_client = ExerciseClient()

    def analyze_performance_plateaus(self, workout_history):
        # Format history for AI
        history_summary = json.dumps(workout_history)
        prompt = f"""
        Sen profesyonel bir fitness analistisin. Kullanıcının antrenman geçmişini analiz et:
        {history_summary}

        GÖREV:
        1. Hangi egzersizlerde ilerleme durmuş (plateau)?
        2. Hangi kas grupları ihmal edilmiş veya ilerlemiyor?
        3. Bir deload haftası gerekiyor mu?

        Cevabını kısa, net ve bilimsel bir dille ver.
        """
        return self._call_groq(prompt)

    def orchestrate_fitness_plan(self, user_goal, muscle):
        exercises = self.exercise_client.get_exercises(muscle=muscle)
        if not exercises: return "Egzersiz bulunamadı."
        prompt = f"Hedef: {user_goal}. Egzersizler: {json.dumps(exercises[:5])}. Profesyonelce açıkla."
        return self._call_groq(prompt)
