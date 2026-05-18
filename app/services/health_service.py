from app import db
from app.services.nutrition_service import NutritionService

class HealthService:
    @staticmethod
    def calculate_nutri_score(user, date_obj):
        """
        Calculates NutriScore (0-100) based on adherence to targets.
        """
        summary = NutritionService.get_daily_summary(user, date_obj)
        targets = summary.get('targets', {})
        
        if not targets or targets.get('calories', 0) == 0:
            return 0
            
        # 1. Calorie Score (40 points) - Within +/- 10% is perfect
        cal_diff = abs(summary['calories'] - targets['calories'])
        cal_score = max(0, 40 - (cal_diff / targets['calories'] * 40))
        
        # 2. Protein Score (30 points) - Minimum target is better
        pro_ratio = summary['protein'] / targets['protein'] if targets['protein'] > 0 else 0
        if pro_ratio >= 0.9: pro_score = 30
        else: pro_score = pro_ratio * 30
        
        # 3. Water Score (20 points) - 2500ml is target
        water_score = min(20, (summary['water'] / targets.get('water', 2500)) * 20)
        
        # 4. Macro Balance (10 points) - Simple check
        macro_score = 10 if (summary['carbs'] > 0 and summary['fats'] > 0) else 0
        
        total_score = int(cal_score + pro_score + water_score + macro_score)
        
        # Update profile
        if user.health_profile:
            user.health_profile.last_nutri_score = total_score
            db.session.commit()
            
        return total_score

    @staticmethod
    def update_user_targets(health_profile):
        """
        Calculates and updates targets for a health profile.
        """
        targets = NutritionService.calculate_targets(health_profile)
        
        health_profile.target_calories = int(targets['calories'])
        health_profile.target_protein = round(targets['protein'], 1)
        health_profile.target_carbs = round(targets['carbs'], 1)
        health_profile.target_fats = round(targets['fats'], 1)
        
        db.session.add(health_profile)
        db.session.commit()
        
        return health_profile
