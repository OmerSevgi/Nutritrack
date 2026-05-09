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
            
            # Miktarı ve birimi ayıkla (Örn: "4 adet", "150g", "2 porsiyon")
            raw_qty_str = str(item.get('miktar') or item.get('quantity') or '1').lower()
            num_match = re.search(r"(\d+\.?\d*)", raw_qty_str)
            num_val = float(num_match.group(1)) if num_match else 1.0
            
            # Birim kontrolü
            is_weight = any(unit in raw_qty_str for unit in ['g', 'gram', 'ml', 'kg', 'lt'])
            
            # AI'dan gelen toplam kaloriyi al
            total_cal = float(item.get('kalori') or 0)
            total_pro = float(item.get('protein') or 0)
            total_carb = float(item.get('karbonhidrat') or 0)
            total_fat = float(item.get('yag') or 0)

            # Mevcut "summary_service" mantığına (qty < 20 kuralı) uyum sağla:
            if is_weight:
                # Eğer gram cinsindense ve 20'den büyükse, FoodItem'da 100g değerini tutmalıyız
                # Çünkü summary_service: qty >= 20 ise (qty/100 * calories) yapar.
                if num_val >= 20:
                    norm_factor = num_val / 100.0
                else:
                    # 20g altındaysa summary_service doğrudan (qty * calories) yapar.
                    norm_factor = num_val
                
                qty_to_log = num_val
            else:
                # Adet/Tane ise summary_service doğrudan (qty * calories) yapar.
                # Bu yüzden FoodItem'da 1 adet değerini tutmalıyız.
                norm_factor = num_val
                qty_to_log = num_val

            # Değerleri normalize et (Eğer toplam değerler gelmişse)
            if total_cal > 0:
                cal_norm = total_cal / norm_factor if norm_factor > 0 else 0
                pro_norm = total_pro / norm_factor if norm_factor > 0 else 0
                carb_norm = total_carb / norm_factor if norm_factor > 0 else 0
                fat_norm = total_fat / norm_factor if norm_factor > 0 else 0
            else:
                # Eğer AI değer dönmediyse API'den çek (API her zaman 100g değerini döner)
                ninjas_client = CalorieNinjasClient()
                api_data = ninjas_client.get_nutrition(name)
                nutrition = api_data[0] if api_data else {}
                cal_norm = float(nutrition.get('calories', 0))
                pro_norm = float(nutrition.get('protein_g', 0))
                carb_norm = float(nutrition.get('carbohydrates_total_g', 0))
                fat_norm = float(nutrition.get('fat_total_g', 0))
                # Eğer adetse ve API 100g döndüyse, bir adet tahmini ağırlıkla (örn 50g) çarpılabilir
                # Ama şimdilik API'den gelen 100g bazını koruyoruz.

            # FoodItem kaydet/güncelle
            food = FoodItem.query.filter(FoodItem.name.ilike(name)).first()
            if not food:
                food = FoodItem(
                    name=name,
                    calories=cal_norm,
                    protein=pro_norm,
                    carbs=carb_norm,
                    fats=fat_norm
                )
                db.session.add(food)
                db.session.flush()
            
            entry = LogEntry(daily_log_id=log.id, food_item_id=food.id, quantity=qty_to_log, meal_type='auto', prompt_text=text)
            db.session.add(entry)
            logged_items.append({"name": name, "quantity": qty_to_log, "unit": "g" if is_weight else "adet"})
        
        db.session.commit()
        return logged_items
