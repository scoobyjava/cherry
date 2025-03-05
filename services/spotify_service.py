import requests
from config import SPOTIFY_API_KEY

class SpotifyService:
    def __init__(self):
        self.api_key = SPOTIFY_API_KEY
        self.base_url = 'https://api.spotify.com/v1'

    def get_user_profile(self):
        headers = {
            'Authorization': f'Bearer {self.api_key}'
        }
        response = requests.get(f'{self.base_url}/me', headers=headers)
        return response.json()
