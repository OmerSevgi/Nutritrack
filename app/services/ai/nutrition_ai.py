import json
from app.services.ai.base_service import AIBaseService
from app.integrations.spoonacular_client import SpoonacularClient

class NutritionAIService(AIBaseService):
    def __init__(self):
        super().__init__()
        self.spoonacular = SpoonacularClient()

    def parse_food_input(self, text):
        system_prompt = """
        Sen uzman bir diyetisyen ve veri mühendisisin. Görevin, kullanıcıdan gelen besin girdilerini analiz etmektir.
        Sadece JSON döndür: {"besinler": [{"ad": "Besin Adı", "miktar": "150g", "kalori": 165, "protein": 31, "karbonhidrat": 0, "yag": 3.6}]}
        """
        raw_json = self._call_gemini(f"{system_prompt}\nMetin: {text}")
        try:
            return json.loads(raw_json).get("besinler", [])
        except:
            return []

    def generate_fridge_recipe(self, user_goal, ingredients):
        prompt = f"Hedef: {user_goal}. Malzemeler: {ingredients}. Sağlıklı bir tarif üret ve makro değerlerini ekle."
        return self._call_groq(prompt)

    def get_recipe_suggestions(self, ingredients):
        recipes = self.spoonacular.find_recipes(ingredients)
        if not recipes: return "Uygun tarif bulunamadı."
        prompt = f"Bulunan tarifler: {json.dumps(recipes)}. Bunları kullanıcının hedefine uygun seç ve kısa tariflerini ver."
        return self._call_groq(prompt)
