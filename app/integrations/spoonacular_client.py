import os
import requests
from flask import current_app

class SpoonacularClient:
    def __init__(self):
        self.api_key = os.environ.get('SPOONACULAR_API_KEY')
        self.base_url = "https://api.spoonacular.com"

    def find_recipes(self, ingredients=None, calories=None):
        url = f"{self.base_url}/recipes/findByIngredients"
        params = {
            'apiKey': self.api_key,
            'ingredients': ingredients,
            'number': 3
        }
        response = requests.get(url, params=params)
        return response.json() if response.status_code == 200 else []
