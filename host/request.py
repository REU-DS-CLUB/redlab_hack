import requests

def get_marc(start_dt, end_dt):
    url = f"http://80.87.104.231:8000/handlers/global_detection?start_dt={start_dt}&end_dt={end_dt}"
    
    response = requests.get(url, verify= False)
    print("*"*100)
    print(response)
    return response

def get_new_anomalies(start_dt, end_dt):
    url = f"http://80.87.104.231:8000/handlers/local_detection?start_dt={start_dt}&end_dt={end_dt}"
    
    response = requests.get(url, verify= False)
    print("*"*100)
    print(response)
    return response