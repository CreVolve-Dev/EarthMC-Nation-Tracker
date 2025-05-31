import requests

def get_api_data(endPoint):
    url = f'https://api.earthmc.net/v3/aurora{endPoint}'

    response = requests.get(url)
    data = response.json()

    return data