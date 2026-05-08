from app.models.nutrition import DailyLog, LogEntry
from datetime import datetime

class NutritionService:
    @staticmethod
    def calculate_bmr(gender, weight, height, age):
        """
        Calculate BMR using Mifflin-St Jeor Equation.
        Weight in kg, height in cm, age in years.
        """
        if not all([gender, weight, height, age]):
            return 0
            
        if gender.lower() == 'male':
            return (10 * weight) + (6.25 * height) - (5 * age) + 5
        else:
            return (10 * weight) + (6.25 * height) - (5 * age) - 161

    @staticmethod
    def calculate_tdee(bmr, activity_level):
        """
        Calculate TDEE based on activity level.
        """
        multipliers = {
            'sedentary': 1.2,
            'lightly_active': 1.375,
            'moderately_active': 1.55,
            'very_active': 1.725,
            'extra_active': 1.9
        }
        return bmr * multipliers.get(activity_level, 1.2)

    @staticmethod
    def calculate_targets(health_profile):
        """
        Calculate daily calorie and macro targets based on goal.
        Goal: hypertrophy, fat_loss, maintenance
        """
        bmr = NutritionService.calculate_bmr(
            health_profile.gender,
            health_profile.weight,
            health_profile.height,
            health_profile.age
        )
        tdee = NutritionService.calculate_tdee(bmr, health_profile.activity_level)
        
        targets = {
            'calories': tdee,
            'protein': health_profile.weight * 1.0, # Default
            'carbs': 0,
            'fats': 0
        }
        
        if health_profile.goal == 'hypertrophy':
            # 1.8-2.2g protein per kg. Let's aim for 2.0g as midpoint
            targets['protein'] = health_profile.weight * 2.0
            # Calorie surplus for hypertrophy (usually 250-500 kcal)
            targets['calories'] = tdee + 300
        elif health_profile.goal == 'fat_loss':
            targets['protein'] = health_profile.weight * 2.2 # Higher protein to preserve muscle
            targets['calories'] = tdee - 500
        else: # maintenance
            targets['protein'] = health_profile.weight * 1.6
            targets['calories'] = tdee
            
        # Macro distribution (typical: 25-30% fat, rest carbs)
        # Protein is 4 kcal/g, Fat is 9 kcal/g, Carb is 4 kcal/g
        protein_kcal = targets['protein'] * 4
        
        targets['fats'] = (targets['calories'] * 0.25) / 9 # 25% from fat
        fat_kcal = targets['fats'] * 9
        
        targets['carbs'] = (targets['calories'] - protein_kcal - fat_kcal) / 4
        
        return targets

    @staticmethod
    def get_daily_summary(user, date_obj):
        """
        Calculates total nutrition for a specific user and date, grouping by meal (prompt).
        """
        log = DailyLog.query.filter_by(user_id=user.id, date=date_obj).first()
        
        summary = {
            'calories': 0,
            'protein': 0,
            'carbs': 0,
            'fats': 0,
            'water': 0,
            'meals': [], # Grouped entries
            'targets': {
                'calories': user.health_profile.target_calories if user.health_profile else 0,
                'protein': user.health_profile.target_protein if user.health_profile else 0,
                'carbs': user.health_profile.target_carbs if user.health_profile else 0,
                'fats': user.health_profile.target_fats if user.health_profile else 0,
                'water': 2500 # Default target in ml
            }
        }
        
        if log:
            summary['water'] = log.water_intake or 0
            
            # Temporary dict to group entries by prompt_text
            meal_groups = {}
            
            for entry in log.entries:
                f = entry.food_item
                # Since we normalized to 'unit' or 'per 100g' in the route:
                if entry.quantity < 20:
                    q_ratio = entry.quantity # 4 adet -> * 4
                else:
                    q_ratio = entry.quantity / 100.0 # 200g -> * 2
                
                cal = (f.calories or 0) * q_ratio
                pro = (f.protein or 0) * q_ratio
                carb = (f.carbs or 0) * q_ratio
                fat = (f.fats or 0) * q_ratio
                
                summary['calories'] += cal
                summary['protein'] += pro
                summary['carbs'] += carb
                summary['fats'] += fat
                
                # Grouping key: either prompt_text or entry.id (for manual)
                group_key = entry.prompt_text if entry.prompt_text else f"manual_{entry.id}"
                
                if group_key not in meal_groups:
                    meal_groups[group_key] = {
                        'id': entry.id, # Using first entry ID as reference
                        'title': entry.prompt_text if entry.prompt_text else f.name,
                        'total_calories': 0,
                        'total_protein': 0,
                        'is_ai': entry.prompt_text is not None,
                        'items': []
                    }
                
                meal_groups[group_key]['total_calories'] += round(cal, 1)
                meal_groups[group_key]['total_protein'] += round(pro, 1)
                meal_groups[group_key]['items'].append({
                    'id': entry.id,
                    'name': f.name,
                    'quantity': entry.quantity,
                    'is_count': entry.quantity < 20,
                    'unit_calories': f.calories,
                    'unit_protein': f.protein,
                    'total_calories': round(cal, 1),
                    'total_protein': round(pro, 1),
                })
            
            # Convert groups to list and round totals
            for g in meal_groups.values():
                g['total_calories'] = round(g['total_calories'], 1)
                g['total_protein'] = round(g['total_protein'], 1)
                summary['meals'].append(g)
        
        # Round values for clean output
        for key in ['calories', 'protein', 'carbs', 'fats']:
            summary[key] = round(summary[key], 1)
            
        return summary

    @staticmethod
    def get_weekly_history(user):
        """
        Returns calorie totals for the last 7 days.
        """
        from datetime import timedelta
        end_date = datetime.utcnow().date()
        start_date = end_date - timedelta(days=6)
        
        history = []
        current_date = start_date
        while current_date <= end_date:
            log = DailyLog.query.filter_by(user_id=user.id, date=current_date).first()
            total_cal = 0
            if log:
                for entry in log.entries:
                    total_cal += (entry.food_item.calories or 0) * (entry.quantity / 100.0)
            
            history.append({
                'date': current_date.strftime('%d %b'),
                'calories': round(total_cal, 0)
            })
            current_date += timedelta(days=1)
            
        return history
