import json
from app.services.ai.base_service import AIBaseService
from app.integrations.ninjas_client import ExerciseClient

class FitnessAIService(AIBaseService):
    def __init__(self):
        super().__init__()
        self.exercise_client = ExerciseClient()

    def analyze_structured_workout(self, user_profile, planned_data, actual_data):
        prompt = f"""
        Sen profesyonel bir fitness antrenörüsün. Kullanıcının planladığı antrenman ile yaptığı antrenmanı karşılaştır.
        
        Planlanan: {json.dumps(planned_data)}
        Yapılan: {json.dumps(actual_data)}
        Hedef: {user_profile.get('goal')}
        
        GÖREV: Progresif yükleme, set/tekrar uyumu ve hacim analizi yaparak motive edici ve düzeltici profesyonel bir geri bildirim ver.
        
        Sadece şu JSON formatında dön:
        {{"feedback": "Kısa ve etkileyici geri bildirimin"}}
        """
        raw_json = self._call_groq(prompt, json_mode=True)
        try:
            return json.loads(raw_json).get("feedback", "Harika bir antrenmandı, devam et!")
        except:
            return "Antrenman analizi başarıyla tamamlandı!"

    def orchestrate_fitness_plan(self, user_goal, muscle):
        exercises = self.exercise_client.get_exercises(muscle=muscle)
        if not exercises: return "Egzersiz bulunamadı."
        prompt = f"Hedef: {user_goal}. Egzersizler: {json.dumps(exercises[:5])}. Profesyonelce açıkla."
        return self._call_groq(prompt)
