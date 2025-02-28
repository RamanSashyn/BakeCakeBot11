import requests
import random
import string
from urllib.parse import urlparse


ACCESS_TOKEN = "1fe567ad1fe567ad1fe567adf51cce744a11fe51fe567ad785a30ef24c275e663c9b6b6"


def generate_vk_short_link(original_url):
    api_url = "https://api.vk.com/method/utils.getShortLink"

    unique_param = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
    unique_url = f"{original_url}?unique={unique_param}"

    params = {
        'url': unique_url,
        'access_token': ACCESS_TOKEN,
        'v': '5.199'
    }

    response = requests.get(api_url, params=params)
    response.raise_for_status()

    response_data = response.json()

    if "error" in response_data:
        error_message = response_data["error"].get(
            "error_msg", "Неизвестная ошибка"
        )
        error_code = response_data["error"].get(
            "error_code", "Неизвестный код ошибки"
        )
        raise ValueError(
            f"Ошибка VK API: {error_message} (Код ошибки: {error_code})"
        )

    return response_data["response"]["short_url"]


def count_clicks(
    ACCESS_TOKEN, short_url, interval="day", intervals_count=1, extended=0
):
    parsed_url = urlparse(short_url)
    key = parsed_url.path.split("/")[-1]

    url = "https://api.vk.com/method/utils.getLinkStats"
    params = {
        "access_token": ACCESS_TOKEN,
        "v": "5.199",
        "key": key,
        "interval": interval,
        "intervals_count": intervals_count,
        "extended": extended,
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()

        if "error" in data:
            print(f"Ошибка VK API: {data['error']['error_msg']}")
            return 0

        stats = data.get("response", {}).get("stats", [])
        if stats:
            return [stat['views'] for stat in stats]
        else:
            return []
    except requests.exceptions.RequestException as e:
        print(f"Ошибка при запросе к VK API: {e}")
        return []
