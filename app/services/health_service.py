from app import db
from app.services.nutrition_service import NutritionService

class HealthService:
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
