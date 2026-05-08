import os

import requests


base_url = os.getenv("HTTP_STATUS_BASE_URL", "https://httpstat.us")
status_codes = [102, 200, 302, 404, 500]
timeout_seconds = 10


def make_request(status_code):
    url = f"{base_url.rstrip('/')}/{status_code}"

    print("request url:", url)

    try:
        response = requests.get(url, timeout=timeout_seconds, allow_redirects=False)

        body = response.text.strip()

        if len(body) > 200:
            body = body[:200] + "..."

        print("status code:", response.status_code)
        print("body:", body)
        print("-" * 40)
    except requests.RequestException as error:
        print("request error:", error)
        print("-" * 40)


def main():
    for status_code in status_codes:
        make_request(status_code)


if __name__ == "__main__":
    main()