from app.models.nutrition import DailyLog
from datetime import datetime, timedelta

class NutritionSummaryService:
    @staticmethod
    def get_daily_summary(user, date_obj):
        log = DailyLog.query.filter_by(user_id=user.id, date=date_obj).first()
        summary = {
            'calories': 0, 'protein': 0, 'carbs': 0, 'fats': 0, 'water': 0, 'meals': [],
            'targets': {
                'calories': user.health_profile.target_calories if user.health_profile else 0,
                'protein': user.health_profile.target_protein if user.health_profile else 0,
                'carbs': user.health_profile.target_carbs if user.health_profile else 0,
                'fats': user.health_profile.target_fats if user.health_profile else 0,
                'water': 2500
            }
        }
        
        if log:
            summary['water'] = log.water_intake or 0
            meal_groups = {}
            for entry in log.entries:
                f = entry.food_item
                q_ratio = entry.quantity if entry.quantity < 20 else entry.quantity / 100.0
                
                cal = (f.calories or 0) * q_ratio
                pro = (f.protein or 0) * q_ratio
                
                summary['calories'] += cal
                summary['protein'] += pro
                summary['carbs'] += (f.carbs or 0) * q_ratio
                summary['fats'] += (f.fats or 0) * q_ratio
                
                group_key = entry.prompt_text if entry.prompt_text else f"manual_{entry.id}"
                if group_key not in meal_groups:
                    meal_groups[group_key] = {
                        'id': entry.id, 'title': entry.prompt_text if entry.prompt_text else f.name,
                        'total_calories': 0, 'total_protein': 0, 'items': []
                    }
                meal_groups[group_key]['total_calories'] += round(cal, 1)
                meal_groups[group_key]['total_protein'] += round(pro, 1)
                meal_groups[group_key]['items'].append({'name': f.name, 'quantity': entry.quantity, 'total_calories': round(cal, 1)})
            
            summary['meals'] = list(meal_groups.values())

        for key in ['calories', 'protein', 'carbs', 'fats']: summary[key] = round(summary[key], 1)
        return summary

    @staticmethod
    def get_weekly_history(user):
        end_date = datetime.utcnow().date()
        history = []
        for i in range(6, -1, -1):
            date = end_date - timedelta(days=i)
            log = DailyLog.query.filter_by(user_id=user.id, date=date).first()
            cal = sum([(e.food_item.calories or 0) * (e.quantity / 100.0) for e in log.entries]) if log else 0
            history.append({'date': date.strftime('%d %b'), 'calories': round(cal, 0)})
        return history
