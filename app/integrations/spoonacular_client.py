import os
import requests
from flask import current_app

class SpoonacularClient:
    def __init__(self):
        self.api_key = os.environ.get('SPOONACULAR_API_KEY')
        self.base_url = "https://api.spoonacular.com"

    def find_recipes(self, ingredients):
        try:
            url = f"{self.base_url}/recipes/findByIngredients"
            params = {'apiKey': self.api_key, 'ingredients': ingredients, 'number': 3}
            response = requests.get(url, params=params)
            return response.json() if response.status_code == 200 else []
        except Exception as e:
            print(f"Error fetching recipes: {e}")
            return []

    def get_recipe_by_calories(self, target_calories):
        try:
            url = f"{self.base_url}/recipes/mealplans/generate"
            params = {'apiKey': self.api_key, 'targetCalories': target_calories, 'timeFrame': 'day'}
            response = requests.get(url, params=params)
            return response.json() if response.status_code == 200 else None
        except Exception as e:
            print(f"Error fetching recipes by calories: {e}")
            return None
