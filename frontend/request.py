import requests
import base64

def get_token(email, password, login_url):

    credentials = base64.b64encode(f"{email}:{password}".encode()).decode()
    headers = {
        'Authorization': f'Basic {credentials}',
        'Content-Type': 'application/json'
    }
    response = requests.post(login_url, headers=headers)
    if response.status_code != 200:
        print(f"Login failed with status {response.status_code}")
        print(f"Response: {response.text}")
        
    response.raise_for_status()
    return response.json()['access_token']

def api_request(url, token):
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()