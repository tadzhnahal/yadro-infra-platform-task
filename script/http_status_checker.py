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

    response = requests.get(url, timeout=timeout_seconds, allow_redirects=False)

    body = response.text.strip()

    if len(body) > 200:
        body = body[:200] + "..."

    if 100 <= response.status_code < 400:
        logging.info(
            "successful response: requested_status_code=%s, actual_status_code=%s, body=%s",
            status_code,
            response.status_code,
            body,
        )
        return

    if 400 <= response.status_code < 600:
        raise Exception(
            f"bad response: requested_status_code={status_code}, "
            f"actual_status_code={response.status_code}, body={body!r}"
        )

    raise Exception(
        f"unexpected response: requested_status_code={status_code}, "
        f"actual_status_code={response.status_code}, body={body!r}"
    )


def main():
    for status_code in status_codes:
        try:
            make_request(status_code)
        except requests.RequestException as error:
            logging.error(
                "request failed: requested_status_code=%s, error=%s",
                status_code,
                error,
            )
        except Exception as error:
            logging.error("status check failed: %s", error)

        logging.info("-" * 40)


if __name__ == "__main__":
    main()
