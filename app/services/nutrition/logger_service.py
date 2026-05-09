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
            
            # Sadece sayısal kısmı ayıkla (Basit mantığa dönüş)
            raw_qty = str(item.get('miktar') or item.get('quantity') or '1')
            match = re.search(r"(\d+\.?\d*)", raw_qty)
            qty = float(match.group(1)) if match else 1.0
            
            # Pirinç türevlerini standartlaştır
            search_name = name.lower()
            rice_variants = ['pirinç', 'toz pirinç', 'cream rice', 'rice cream', 'pirinc']
            if any(variant in search_name for variant in rice_variants):
                search_name = "raw rice"
            else:
                search_name = name

            food = FoodItem.query.filter(FoodItem.name.ilike(search_name)).first()
            if not food:
                api_data = ninjas_client.get_nutrition(search_name)
                nutrition = api_data[0] if api_data else {}
                food = FoodItem(
                    name=name,
                    calories=item.get('kalori') or nutrition.get('calories', 0),
                    protein=item.get('protein') or nutrition.get('protein_g', 0),
                    carbs=item.get('karbonhidrat') or nutrition.get('carbohydrates_total_g', 0),
                    fats=item.get('yag') or nutrition.get('fat_total_g', 0)
                )
                db.session.add(food)
                db.session.flush()
            
            entry = LogEntry(daily_log_id=log.id, food_item_id=food.id, quantity=qty, meal_type='auto', prompt_text=text)
            db.session.add(entry)
            logged_items.append({"name": name, "quantity": qty})
        
        db.session.commit()
        return logged_items
