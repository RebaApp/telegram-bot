import telebot
import json
import os
import logging
import time
import traceback
from datetime import datetime

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

TOKEN = os.getenv("BOT_TOKEN")

if not TOKEN:
    logger.error("BOT_TOKEN не найден в переменных окружения!")
    exit(1)

bot = telebot.TeleBot(TOKEN)

USERS_FILE = "users.json"
STATE_FILE = "state.json"
MOTIVATIONS_FILE = "motivations.json"

def load_users():
    try:
        if os.path.exists(USERS_FILE):
            with open(USERS_FILE, "r", encoding="utf-8") as f:
                users = json.load(f)
                logger.info(f"Загружено {len(users)} пользователей")
                return users
        else:
            logger.info("Файл пользователей не найден, создаю новый")
            return []
    except Exception as e:
        logger.error(f"Ошибка загрузки пользователей: {e}")
        return []

def save_users(users):
    try:
        with open(USERS_FILE, "w", encoding="utf-8") as f:
            json.dump(users, f, ensure_ascii=False, indent=2)
        logger.info(f"Сохранено {len(users)} пользователей")
    except Exception as e:
        logger.error(f"Ошибка сохранения пользователей: {e}")

def load_state():
    try:
        if os.path.exists(STATE_FILE):
            with open(STATE_FILE, "r", encoding="utf-8") as f:
                state = json.load(f)
                logger.info(f"Загружено состояние: индекс {state.get('index', 0)}")
                return state
        else:
            logger.info("Файл состояния не найден, создаю новый")
            return {"index": 0}
    except Exception as e:
        logger.error(f"Ошибка загрузки состояния: {e}")
        return {"index": 0}

def save_state(state):
    try:
        with open(STATE_FILE, "w", encoding="utf-8") as f:
            json.dump(state, f, ensure_ascii=False, indent=2)
        logger.info(f"Сохранено состояние: индекс {state.get('index', 0)}")
    except Exception as e:
        logger.error(f"Ошибка сохранения состояния: {e}")

def load_motivations():
    try:
        if os.path.exists(MOTIVATIONS_FILE):
            with open(MOTIVATIONS_FILE, "r", encoding="utf-8") as f:
                motivations = json.load(f)
                logger.info(f"Загружено {len(motivations)} мотивационных цитат")
                return motivations
        else:
            logger.error("Файл мотиваций не найден!")
            return []
    except Exception as e:
        logger.error(f"Ошибка загрузки мотиваций: {e}")
        return []

@bot.message_handler(commands=["start"])
def start(message):
    try:
        users = load_users()
        if message.chat.id not in users:
            users.append(message.chat.id)
            save_users(users)
            bot.send_message(message.chat.id, "Ты подписался на ежедневные цитаты. Жди первую завтра!")
            logger.info(f"Новый пользователь подписался: {message.chat.id}")
        else:
            bot.send_message(message.chat.id, "Ты уже подписан.")
            logger.info(f"Пользователь уже подписан: {message.chat.id}")
    except Exception as e:
        logger.error(f"Ошибка в команде start: {e}")
        try:
            bot.send_message(message.chat.id, "Произошла ошибка. Попробуйте позже.")
        except:
            pass

def send_motivation():
    try:
        logger.info("Начинаю отправку мотивационных сообщений")
        users = load_users()
        state = load_state()
        motivations = load_motivations()

        if not motivations:
            logger.error("Нет мотивационных цитат для отправки!")
            return

        if not users:
            logger.info("Нет подписчиков для отправки")
            return

        quote = motivations[state["index"] % len(motivations)]
        logger.info(f"Отправляю цитату #{state['index']}: {quote[:50]}...")
        
        successful_sends = 0
        failed_sends = 0
        
        for user in users[:]:  # Используем копию списка для безопасного удаления
            try:
                time.sleep(0.5)  # Небольшая задержка между отправками
                bot.send_message(user, quote)
                successful_sends += 1
                logger.info(f"Сообщение отправлено пользователю {user}")
            except Exception as e:
                failed_sends += 1
                logger.error(f"Ошибка отправки пользователю {user}: {e}")
                logger.error(f"Детали ошибки: {traceback.format_exc()}")
                # Удаляем неактивных пользователей
                error_str = str(e).lower()
                if "chat not found" in error_str or "user is deactivated" in error_str or "blocked" in error_str:
                    logger.info(f"Удаляю неактивного пользователя {user}")
                    try:
                        users.remove(user)
                    except ValueError:
                        pass

        # Сохраняем обновленный список пользователей
        if failed_sends > 0:
            save_users(users)

        state["index"] += 1
        save_state(state)
        
        logger.info(f"Отправка завершена. Успешно: {successful_sends}, Ошибок: {failed_sends}")
        
    except Exception as e:
        logger.error(f"Критическая ошибка в send_motivation: {e}")

@bot.message_handler(commands=["stats"])
def stats(message):
    try:
        users = load_users()
        state = load_state()
        motivations = load_motivations()
        
        stats_text = f"""📊 Статистика бота:
👥 Подписчиков: {len(users)}
📝 Всего цитат: {len(motivations)}
🔄 Текущий индекс: {state['index']}
📅 Последняя отправка: {datetime.now().strftime('%d.%m.%Y %H:%M')}"""
        
        bot.send_message(message.chat.id, stats_text)
        logger.info(f"Статистика запрошена пользователем {message.chat.id}")
    except Exception as e:
        logger.error(f"Ошибка в команде stats: {e}")
        try:
            bot.send_message(message.chat.id, "Произошла ошибка при получении статистики.")
        except:
            pass

if __name__ == "__main__":
    logger.info("Запуск бота для отправки мотивационных сообщений")
    
    # Диагностическая информация
    token_exists = bool(os.getenv("BOT_TOKEN"))
    logger.info(f"BOT_TOKEN присутствует: {token_exists}")
    
    try:
        send_motivation()
        logger.info("Бот успешно завершил работу")
        exit(0)
    except Exception as e:
        logger.error(f"Критическая ошибка при запуске бота: {e}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        exit(1)
