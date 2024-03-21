import os
import requests
import json

def get_new_access_token(refresh_token):
    body = {"refresh_token": refresh_token,
            "grant_type": "refresh_token",
            "scope": "app"}
    oauth_api_key =  os.getenv("API_GEN_REFRESH_TOKEN_KEY")
    headers = {'Authorization': oauth_api_key}
    new_acces_token_url = os.getenv("API_GEN_REFRESH_TOKEN_URL")
    response = requests.post(new_acces_token_url, json=body, headers=headers)
    if response.status_code == 200:
        parsed_response = json.loads(response.text)
        return parsed_response["access_token"]
