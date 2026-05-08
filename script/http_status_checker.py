import os

import requests


base_url = os.getenv("HTTP_STATUS_BASE_URL", "https://httpstat.us")
url = f"{base_url}/200"

try:
    response = requests.get(url, timeout=10)

    print("status code:", response.status_code)
    print("body:", response.text.strip())
except requests.RequestException as error:
    print("request error:", error)