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

    def analyze_structured_workout(self, user_profile, planned_data, actual_data):
        prompt = f"""
        Sen bir profesyonel fitness koçusun. Kullanıcının antrenman performansını analiz et.
        
        Kullanıcı Hedefi: {user_profile.get('goal')}
        Planlanan Program: {json.dumps(planned_data, ensure_ascii=False)}
        Gerçekleşen Antrenman: {json.dumps(actual_data, ensure_ascii=False)}
        
        GÖREV:
        1. Kullanıcının planlanan set ve tekrarlara ne kadar uyduğunu değerlendir.
        2. İlerleme (progressive overload) belirtilerini yakala.
        3. Bir sonraki antrenman için kısa ve bilimsel bir tavsiye ver.
        
        Cevabı bir paragrafta, motive edici ve profesyonel bir dille ver.
        """
        return self._call_groq(prompt)
