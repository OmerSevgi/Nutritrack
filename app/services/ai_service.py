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
    def ask_coach(self, query): return self.nutrition._call_groq(query)
    def orchestrate_fitness_plan(self, goal, muscle): return self.fitness.orchestrate_fitness_plan(goal, muscle)
    def get_recipe_suggestions(self, ing): return self.nutrition.get_recipe_suggestions(ing)
    def generate_weekly_fitness_report(self, prof, stats):
        prompt = f"Haftalık spor raporu özeti hazırla: {stats}"
        return self.fitness._call_groq(prompt)
