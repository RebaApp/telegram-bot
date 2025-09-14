import os
import json
import requests
from datetime import datetime

TOKEN = os.environ["TELEGRAM_TOKEN"]
API_URL = f"https://api.telegram.org/bot{TOKEN}"

# Загружаем пользователей
if os.path.exists("users.json"):
    with open("users.json", "r") as f:
        users = json.load(f)
else:
    users = []

# Загружаем цитаты
with open("motivations.json", "r") as f:
    motivations = json.load(f)

# Загружаем state
if os.path.exists("state.json"):
    with open("state.json", "r") as f:
        state = json.load(f)
else:
    state = {"last_update_id": 0}

# Функция отправки сообщений
def send_message(chat_id, text):
    url = f"{API_URL}/sendMessage"
    data = {"chat_id": chat_id, "text": text}
    requests.post(url, data=data)

# Проверяем новые сообщения (для /start)
updates = requests.get(f"{API_URL}/getUpdates?offset={state['last_update_id']+1}").json()

for update in updates.get("result", []):
    state["last_update_id"] = update["update_id"]
    message = update.get("message", {})
    chat_id = message.get("chat", {}).get("id")
    text = message.get("text", "")

    if text == "/start" and chat_id not in users:
        users.append(chat_id)
        send_message(chat_id, "Ты подписан на ежедневную мотивацию 🔥")

# Определяем сегодняшнюю цитату
day_of_year = datetime.utcnow().timetuple().tm_yday
quote = motivations[(day_of_year - 1) % len(motivations)]

# Рассылаем её всем
for chat_id in users:
    send_message(chat_id, quote)

# Сохраняем пользователей и state
with open("users.json", "w") as f:
    json.dump(users, f)

with open("state.json", "w") as f:
    json.dump(state, f)
