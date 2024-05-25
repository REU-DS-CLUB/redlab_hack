import requests

def get_marc(start_dt, end_dt):
    url = f"80.87.104.231:8000/handlers/simple?start_dt={start_dt}&end_dt={end_dt}"
    
    response = requests.get(url, verify= False)
    return response