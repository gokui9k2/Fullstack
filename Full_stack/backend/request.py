import requests
import base64

def get_token(username, password, url):
    credentials = base64.b64encode(f"{username}:{password}".encode()).decode()
    headers = {"Authorization": f"Basic {credentials}"}
    response = requests.post(url, headers=headers)
    response.raise_for_status()
    return response.json()["access_token"]

def api_request(url, token):
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()


