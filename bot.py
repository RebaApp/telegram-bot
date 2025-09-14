import telebot
import json
import os

TOKEN = os.getenv("BOT_TOKEN")

bot = telebot.TeleBot(TOKEN)

USERS_FILE = "users.json"
STATE_FILE = "state.json"
MOTIVATIONS_FILE = "motivations.json"

def load_users():
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_users(users):
    with open(USERS_FILE, "w", encoding="utf-8") as f:
        json.dump(users, f, ensure_ascii=False, indent=2)

def load_state():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"index": 0}

def save_state(state):
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)

def load_motivations():
    if os.path.exists(MOTIVATIONS_FILE):
        with open(MOTIVATIONS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

@bot.message_handler(commands=["start"])
def start(message):
    users = load_users()
    if message.chat.id not in users:
        users.append(message.chat.id)
        save_users(users)
        bot.send_message(message.chat.id, "Ты подписался на ежедневные цитаты. Жди первую завтра!")
    else:
        bot.send_message(message.chat.id, "Ты уже подписан.")

def send_motivation():
    users = load_users()
    state = load_state()
    motivations = load_motivations()

    if not motivations:
        return

    quote = motivations[state["index"] % len(motivations)]
    for user in users:
        try:
            bot.send_message(user, quote)
        except Exception as e:
            print(f"Ошибка отправки {user}: {e}")

    state["index"] += 1
    save_state(state)

if __name__ == "__main__":
    send_motivation()
