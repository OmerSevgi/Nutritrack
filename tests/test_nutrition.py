import unittest
from app.services.nutrition_service import NutritionService

class TestNutritionService(unittest.TestCase):
    def test_calculate_bmr_male(self):
        # Male, 80kg, 180cm, 25 years
        # (10 * 80) + (6.25 * 180) - (5 * 25) + 5 = 800 + 1125 - 125 + 5 = 1805
        bmr = NutritionService.calculate_bmr('male', 80, 180, 25)
        self.assertEqual(bmr, 1805)

    def test_calculate_bmr_female(self):
        # Female, 60kg, 165cm, 30 years
        # (10 * 60) + (6.25 * 165) - (5 * 30) - 161 = 600 + 1031.25 - 150 - 161 = 1320.25
        bmr = NutritionService.calculate_bmr('female', 60, 165, 30)
        self.assertEqual(bmr, 1320.25)

    def test_hypertrophy_targets(self):
        class MockProfile:
            gender = 'male'
            weight = 80
            height = 180
            age = 25
            activity_level = 'moderately_active'
            goal = 'hypertrophy'
        
        profile = MockProfile()
        targets = NutritionService.calculate_targets(profile)
        
        # BMR 1805, TDEE = 1805 * 1.55 = 2797.75
        # Calorie target = 2797.75 + 300 = 3097.75
        # Protein target = 80 * 2.0 = 160g
        self.assertAlmostEqual(targets['calories'], 3097.75)
        self.assertEqual(targets['protein'], 160)

if __name__ == '__main__':
    unittest.main()
