import requests

def post_api_data(endPoint, query):
    url = f'https://api.earthmc.net/v3/aurora{endPoint}'

    payload = {"query": [query]}

    response = requests.post(url, json=payload)
    data = response.json()

    return data