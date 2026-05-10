from app.services.ai.nutrition_ai import NutritionAIService
from app.services.ai.fitness_ai import FitnessAIService

class AIService:
    """Facade for all AI-related services to maintain backward compatibility."""
    def __init__(self):
        self.nutrition = NutritionAIService()
        self.fitness = FitnessAIService()

    def generate_response(self, user_profile, daily_status, user_query):
        prompt = f"""
        Sen bir koçsun. Profil: {user_profile}. Durum: {daily_status}. Soru: {user_query}.
        Kısa, bilimsel ve motive edici cevap ver.
        """
        return self.nutrition._call_groq(prompt)

    # Proxy methods for backward compatibility
    def parse_food_input(self, text): return self.nutrition.parse_food_input(text)
    def generate_fridge_recipe(self, goal, ing): return self.nutrition.generate_fridge_recipe(goal, ing)
    def analyze_structured_workout(self, prof, planned, actual): return self.fitness.analyze_structured_workout(prof, planned, actual)
    def get_holistic_context(self, user_id):
        # Fetch nutrition summary and fitness performance
        from app.models.nutrition import DailyLog
        from app.models.user_health import Workout
        
        last_logs = DailyLog.query.filter_by(user_id=user_id).order_by(DailyLog.date.desc()).limit(3).all()
        last_workouts = Workout.query.filter_by(user_id=user_id).order_by(Workout.timestamp.desc()).limit(3).all()
        
        context = f"Son beslenme: {[l.summary_text for l in last_logs]}. "
        context += f"Son antrenmanlar: {[w.description for w in last_workouts]}."
        return context

    def ask_coach(self, user_profile, context, query):
        prompt = f"""
        Sen kapsamlı bir sağlık ve fitness koçusun.
        Kullanıcı Bilgileri: {user_profile}
        Güncel Veriler (Beslenme ve Fitness): {context}
        Soru: {query}
        
        Bilimsel, veriye dayalı ve motive edici cevap ver.
        """
        return self.nutrition._call_groq(prompt)
    def orchestrate_fitness_plan(self, goal, muscle): return self.fitness.orchestrate_fitness_plan(goal, muscle)
    def get_recipe_suggestions(self, ing): return self.nutrition.get_recipe_suggestions(ing)
    def generate_weekly_fitness_report(self, prof, stats):
        prompt = f"Haftalık spor raporu özeti hazırla: {stats}"
        return self.fitness._call_groq(prompt)
