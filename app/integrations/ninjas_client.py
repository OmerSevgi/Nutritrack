import os
import requests
from flask import current_app

class APIClient:
    """Base client for API Ninjas / CalorieNinjas APIs."""
    def __init__(self):
        self.api_key = os.environ.get('API_NINJAS_KEY')
        self.base_url = "https://api.api-ninjas.com/v1"

    def _get_headers(self):
        return {'X-Api-Key': self.api_key}

class CalorieNinjasClient(APIClient):
    def get_nutrition(self, query):
        url = f"{self.base_url}/nutritionquery?query={query}"
        response = requests.get(url, headers=self._get_headers())
        return response.json() if response.status_code == 200 else None

class ExerciseClient(APIClient):
    def get_exercises(self, muscle=None, equipment=None):
        params = {}
        if muscle: params['muscle'] = muscle
        if equipment: params['equipment'] = equipment
        
        url = f"{self.base_url}/exercises"
        response = requests.get(url, headers=self._get_headers(), params=params)
        return response.json() if response.status_code == 200 else []
