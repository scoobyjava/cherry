import requests
from config import SMART_HOME_API_KEY

class SmartHomeService:
    def __init__(self):
        self.api_key = SMART_HOME_API_KEY
        self.base_url = 'https://api.smarthome.com/v1'

    def get_device_status(self, device_id):
        headers = {
            'Authorization': f'Bearer {self.api_key}'
        }
        response = requests.get(f'{self.base_url}/devices/{device_id}', headers=headers)
        return response.json()
