import requests

BASE_URL = "http://127.0.0.1:8000/api/"


def authentication():
    return ("discordbot", "3Z2WzDYpSNll2JuE82Wl")
    
    
def build_connection(prefix):
    return BASE_URL + prefix
    
def build(base_url, data):
    return requests.post(base_url, json= data, auth= authentication())
    

def execute(prefix, data):
	try:
		response = build(base_url= build_connection(prefix), data= data)
		return response.json()
  
	except Exception as e:
		print(e)
  