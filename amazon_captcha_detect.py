import requests


URL = "https://www.amazon.com/dp/B096N2MV3H"

CAPTCHA_MARKERS = [
    "Type the characters you see in this image",
    "To discuss automated access to Amazon data",
    "/captcha/",
]


def looks_like_captcha(html: str) -> bool:
    lower = html.lower()
    return any(marker.lower() in lower for marker in CAPTCHA_MARKERS)


def fetch_with_captcha_detection(url: str) -> requests.Response:
    resp = requests.get(url, timeout=30)
    print("Status:", resp.status_code)

    if looks_like_captcha(resp.text):
        print("[WARN] This response looks like a CAPTCHA / bot-check page.")
    else:
        print("[INFO] This response looks like a normal page.")
    return resp


def main() -> None:
    fetch_with_captcha_detection(URL)


if __name__ == "__main__":
    main()

