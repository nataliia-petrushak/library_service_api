import requests
from django.conf import settings


def notification(message):
    chat_id = settings.CHAT_ID,
    url = f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/sendMessage"
    data = {"chat_id": chat_id, "text": message}
    requests.post(url, data)
