# IFTTT Integration
import requests

IFTTT_KEY = 'your_ifttt_webhook_key'

def trigger_ifttt_event(event, value1=None, value2=None, value3=None):
    url = f"https://maker.ifttt.com/trigger/{event}/with/key/{IFTTT_KEY}"
    data = {"value1": value1, "value2": value2, "value3": value3}
    try:
        requests.post(url, json=data)
    except Exception as e:
        print(f"IFTTT Error: {e}")
