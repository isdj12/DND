import os
import requests
from dotenv import load_dotenv

load_dotenv()
token = os.getenv("BOT_TOKEN")

print(f"Токен: {token}")

if token:
    url = f"https://api.telegram.org/bot{token}/getMe"
    try:
        response = requests.get(url)
        print(f"Статус: {response.status_code}")
        print(f"Ответ: {response.json()}")
    except Exception as e:
        print(f"Ошибка: {e}")
else:
    print("Токен не найден!")