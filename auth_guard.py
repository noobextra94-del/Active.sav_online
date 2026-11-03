import requests

SERVER_URL = "https://admin-panel-af2x.onrender.com"

def verify_license_key(key, hwid):
    try:
        payload = {"key": key, "hwid": hwid}
        res = requests.post(f"{SERVER_URL}/api/verify", json=payload, timeout=10)
        data = res.json()
        return data.get("status", False), data.get("message", "Invalid key")
    except Exception as e:
        return False, str(e)
