import logging
import os

import requests


base_url = os.getenv("HTTP_STATUS_BASE_URL", "https://httpstat.us")
status_codes = [102, 200, 302, 404, 500]
timeout_seconds = 10


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)


def make_request(status_code):
    url = f"{base_url.rstrip('/')}/{status_code}"

    logging.info("request url: %s", url)

    try:
        response = requests.get(url, timeout=timeout_seconds, allow_redirects=False)

        body = response.text.strip()

        if len(body) > 200:
            body = body[:200] + "..."

        logging.info("status code: %s", response.status_code)
        logging.info("body: %s", body)
        logging.info("-" * 40)
    except requests.RequestException as error:
        logging.error("request error: %s", error)
        logging.info("-" * 40)


def main():
    for status_code in status_codes:
        make_request(status_code)


if __name__ == "__main__":
    main()
