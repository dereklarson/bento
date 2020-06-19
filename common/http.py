import requests


def get(api_url)
    try:
        data = requests.get(api_url).json()
        return data
    except Exception:
        logging.warning(f"Issue accessing {api_url}")
