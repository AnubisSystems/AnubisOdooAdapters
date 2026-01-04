import random
import requests

def call_odoo(endpoint, service, method, *args):
    payload = {
            "jsonrpc": "2.0",
            "method": "call",
            "params": {
                "service": service,
                "method": method,
                "args": args
            },
            "id": random.randint(0, 1000000000)
        }
    headers = {"Content-Type": "application/json"}
    print(payload)
    response = requests.post(endpoint, json=payload, headers=headers)
    result = response.json()
    if "error" in result:
        raise Exception(result["error"])
    return result["result"]