from datetime import datetime
from app import db
from app.models.nutrition import FoodItem, DailyLog, LogEntry
from app.integrations.ninjas_client import CalorieNinjasClient
from app.services.ai_service import AIService

class NutritionLoggerService:
    @staticmethod
    def log_manual_meal(user, food_data, quantity, meal_type):
        today = datetime.utcnow().date()
        log = DailyLog.query.filter_by(user_id=user.id, date=today).first()
        if not log:
            log = DailyLog(user_id=user.id, date=today)
            db.session.add(log)
            db.session.flush()
        
        entry = LogEntry(
            daily_log_id=log.id,
            food_item_id=food_data['id'],
            quantity=quantity,
            meal_type=meal_type
        )
        db.session.add(entry)
        db.session.commit()
        return True

    @staticmethod
    def log_ai_meal(user, text):
        ai_service = AIService()
        food_list = ai_service.nutrition.parse_food_input(text)
        if not food_list: return None
        
        ninjas_client = CalorieNinjasClient()
        today = datetime.utcnow().date()
        log = DailyLog.query.filter_by(user_id=user.id, date=today).first()
        if not log:
            log = DailyLog(user_id=user.id, date=today)
            db.session.add(log)
            db.session.flush()

        import re
        logged_items = []
        for item in food_list:
            name = item.get('ad') or item.get('name')
            
            # AI'dan gelen gramaj tahminini al
            raw_qty = str(item.get('miktar') or item.get('quantity') or '100')
            match = re.search(r"(\d+\.?\d*)", raw_qty)
            qty_grams = float(match.group(1)) if match else 100.0
            
            # Pirinç/Pilav kontrolü (Çiğ değer için)
            search_name = name.lower()
            if any(x in search_name for x in ['pirinç', 'pilav', 'rice', 'cream rice']):
                search_name = "raw rice"

            food = FoodItem.query.filter(FoodItem.name.ilike(search_name)).first()
            if not food:
                # API'den her zaman 100g bazlı ham veriyi çek
                api_data = ninjas_client.get_nutrition(search_name)
                nutrition = api_data[0] if api_data else {}
                
                food = FoodItem(
                    name=search_name,
                    calories=float(nutrition.get('calories', 0)),
                    protein=float(nutrition.get('protein_g', 0)),
                    carbs=float(nutrition.get('carbohydrates_total_g', 0)),
                    fats=float(nutrition.get('fat_total_g', 0))
                )
                db.session.add(food)
                db.session.flush()
            
            # Kaydı her zaman gram (qty_grams) olarak yap
            entry = LogEntry(daily_log_id=log.id, food_item_id=food.id, quantity=qty_grams, meal_type='auto', prompt_text=text)
            db.session.add(entry)
            logged_items.append({"name": name, "quantity": qty_grams, "unit": "g"})
        
        db.session.commit()
        return logged_items
