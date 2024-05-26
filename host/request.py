import requests

def get_marc(start_dt, end_dt):
    url = f"http://80.87.104.231:8000/handlers/global_detection?start_dt={start_dt}&end_dt={end_dt}"
    
    response = requests.get(url, verify= False, timeout=30)
    print("*"*100)
    print(response)
    return response

def get_new_anomalies(start_dt, end_dt):
    url = f"http://80.87.104.231:8000/handlers/local_detection?start_dt={start_dt}&end_dt={end_dt}"
    
    response = requests.get(url, verify= False, timeout=30)
    print("*"*100)
    print(response)
    return response

def load_data(path):
    url = 'http://80.87.104.231:8000/handlers/upload'
    file = {'file': open(f'{path}', 'rb')}
    headers = {'Filename': 'path'}
    
    response = requests.post(url, files=file, headers=headers, timeout=None)
    print("*"*100)
    print(response)
    return response