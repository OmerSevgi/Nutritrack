class NutritionCalculator:
    @staticmethod
    def calculate_bmr(gender, weight, height, age):
        if not all([gender, weight, height, age]): return 0
        if gender.lower() == 'male':
            return (10 * weight) + (6.25 * height) - (5 * age) + 5
        return (10 * weight) + (6.25 * height) - (5 * age) - 161

    @staticmethod
    def calculate_tdee(bmr, activity_level):
        multipliers = {
            'sedentary': 1.2, 'lightly_active': 1.375,
            'moderately_active': 1.55, 'very_active': 1.725, 'extra_active': 1.9
        }
        return bmr * multipliers.get(activity_level, 1.2)

    @staticmethod
    def calculate_targets(health_profile):
        bmr = NutritionCalculator.calculate_bmr(
            health_profile.gender, health_profile.weight,
            health_profile.height, health_profile.age
        )
        tdee = NutritionCalculator.calculate_tdee(bmr, health_profile.activity_level)
        
        targets = {'calories': tdee, 'protein': health_profile.weight * 1.0, 'carbs': 0, 'fats': 0}
        
        if health_profile.goal == 'hypertrophy':
            targets['protein'] = health_profile.weight * 2.0
            targets['calories'] = tdee + 300
        elif health_profile.goal == 'fat_loss':
            targets['protein'] = health_profile.weight * 2.2
            targets['calories'] = tdee - 500
        else:
            targets['protein'] = health_profile.weight * 1.6
            targets['calories'] = tdee
            
        targets['fats'] = (targets['calories'] * 0.25) / 9
        targets['carbs'] = (targets['calories'] - (targets['protein'] * 4) - (targets['fats'] * 9)) / 4
        return targets
