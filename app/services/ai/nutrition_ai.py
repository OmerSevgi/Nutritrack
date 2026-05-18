import json
from app.services.ai.base_service import AIBaseService
from app.integrations.spoonacular_client import SpoonacularClient

class NutritionAIService(AIBaseService):
    def __init__(self):
        super().__init__()
        self.spoonacular = SpoonacularClient()

    def parse_food_input(self, text):
        print(f"\n[AI LOG] Requesting parse for: '{text}'")
        system_prompt = """
        Sen uzman bir diyetisyen ve veri mühendisisin.
        GÖREVİN: Kullanıcı metnindeki besinleri analiz et ve her birinin toplam ağırlığını GRAM (g) cinsinden bilimsel ve sektörel standartlara göre tahmin et.
        
        Sadece şu JSON formatında dön:
        {"besinler": [{"ad": "Besin Adı", "en": "English Name", "miktar": "sayısal_gram_değeri", "birim": "g"}]}
        Metin: 
        """
        # Gemini yerine Groq JSON modunu kullanıyoruz
        raw_json = self._call_groq(f"{system_prompt}\n{text}", json_mode=True)
        print(f"[AI LOG] Raw response from Groq: {raw_json}")
        try:
            parsed_data = json.loads(raw_json).get("besinler", [])
            print(f"[AI LOG] Parsed foods: {parsed_data}")
            return parsed_data
        except Exception as e:
            print(f"[AI LOG] Groq parsing error: {e}")
            return []

    def generate_fridge_recipe(self, user_goal, ingredients):
        prompt = f"Hedef: {user_goal}. Malzemeler: {ingredients}. Sağlıklı bir tarif üret ve makro değerlerini ekle."
        return self._call_groq(prompt)

    def get_recipe_suggestions(self, ingredients):
        recipes = self.spoonacular.find_recipes(ingredients)
        if not recipes: return "Uygun tarif bulunamadı."
        prompt = f"Bulunan tarifler: {json.dumps(recipes)}. Bunları kullanıcının hedefine uygun seç ve kısa tariflerini ver."
        return self._call_groq(prompt)

    def get_food_recommendations(self, user_profile, daily_status):
        prompt = f"""
        Kullanıcı Hedefi: {user_profile.get('goal')}
        Günlük Alınan: {daily_status.get('calories')} kcal, {daily_status.get('protein')}g protein
        Hedeflenen: {user_profile.get('target_calories')} kcal, {user_profile.get('target_protein')}g protein
        
        GÖREV:
        Kullanıcının makro hedeflerine ulaşması için bugün tüketebileceği 3 sağlıklı besin önerisi ver.
        Cevabını kısa maddeler halinde ver.
        """
        return self._call_groq(prompt)

    def generate_daily_briefing(self, user_profile, yesterday_stats):
        prompt = f"""
        Dünki Özet: {json.dumps(yesterday_stats)}
        Kullanıcı Hedefi: {user_profile.get('goal')}
        
        GÖREV:
        Kullanıcının dünkü performansını değerlendir ve bugüne özel bir strateji ver.
        Cevabını samimi ve kısa bir paragraf olarak yaz.
        """
        return self._call_groq(prompt)

    def generate_shopping_list(self, user_profile, fitness_stats):
        prompt = f"""
        Hedef: {user_profile.get('goal')}
        Haftalık Toplam Antrenman Hacmi: {fitness_stats.get('total_volume')} kg
        
        GÖREV:
        Kullanıcının bu performans ve hedefi için marketten alması gereken en kritik 5 besini listele.
        Cevabını sadece liste olarak ver.
        """
        return self._call_groq(prompt)
