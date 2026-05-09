from app.services.nutrition.calculator import NutritionCalculator
from app.services.nutrition.summary_service import NutritionSummaryService
from app.services.nutrition.logger_service import NutritionLoggerService

class NutritionService:
    """Facade for nutrition logic."""
    @staticmethod
    def calculate_bmr(g, w, h, a): return NutritionCalculator.calculate_bmr(g, w, h, a)
    
    @staticmethod
    def calculate_tdee(bmr, act): return NutritionCalculator.calculate_tdee(bmr, act)
    
    @staticmethod
    def calculate_targets(hp): return NutritionCalculator.calculate_targets(hp)
    
    @staticmethod
    def get_daily_summary(u, d): return NutritionSummaryService.get_daily_summary(u, d)
    
    @staticmethod
    def get_weekly_history(u): return NutritionSummaryService.get_weekly_history(u)

    @staticmethod
    def log_manual_meal(u, fd, q, mt): return NutritionLoggerService.log_manual_meal(u, fd, q, mt)

    @staticmethod
    def log_ai_meal(u, t): return NutritionLoggerService.log_ai_meal(u, t)
