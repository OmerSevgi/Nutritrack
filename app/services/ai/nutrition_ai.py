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
        GÖREVİN: Sadece geçerli bir JSON objesi döndür.
        JSON FORMATI: {"besinler": [{"ad": "Besin Adı", "miktar": "150g", "kalori": 165, "protein": 31, "karbonhidrat": 0, "yag": 3.6}]}
        Metin: 
        """
        # Gemini yerine Groq JSON modunu kullanıyoruz
        raw_json = self._call_groq(f"{system_prompt}\n{text}", json_mode=True)
        try:
            return json.loads(raw_json).get("besinler", [])
        except Exception as e:
            print(f"Groq parsing error: {e}")
            return []

    def generate_fridge_recipe(self, user_goal, ingredients):
        prompt = f"Hedef: {user_goal}. Malzemeler: {ingredients}. Sağlıklı bir tarif üret ve makro değerlerini ekle."
        return self._call_groq(prompt)

    def get_recipe_suggestions(self, ingredients):
        recipes = self.spoonacular.find_recipes(ingredients)
        if not recipes: return "Uygun tarif bulunamadı."
        prompt = f"Bulunan tarifler: {json.dumps(recipes)}. Bunları kullanıcının hedefine uygun seç ve kısa tariflerini ver."
        return self._call_groq(prompt)
