import logging
import os
import time

import requests
import telegram
from dotenv import load_dotenv

load_dotenv()


PRAKTIKUM_TOKEN = os.getenv("PRAKTIKUM_TOKEN")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")


bot = telegram.Bot(token=TELEGRAM_TOKEN)


logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s, %(levelname)s, %(name)s, %(message)s",
    filename="main.log",
    filemode="w",
)


def parse_homework_status(homework):
    homework_name = homework["homework_name"]
    verdict = None
    try:
        if homework["status"] == "reviewing":
            verdict = "Работа взята на ревью."
        elif homework["status"] == "rejected":
            verdict = "К сожалению, в работе нашлись ошибки."
        else:
            verdict = "Ревьюеру всё понравилось, работа зачтена!"
    except Exception as error:
        logging.error(error, exc_info=True)
    return f'У вас проверили работу "{homework_name}"!\n\n{verdict}'


def get_homeworks(current_timestamp):
    url = "https://praktikum.yandex.ru/api/user_api/homework_statuses/"
    headers = {"Authorization": f"OAuth {PRAKTIKUM_TOKEN}"}
    payload = {"from_date": current_timestamp}
    homework_statuses = requests.get(url, headers=headers, params=payload)
    return homework_statuses.json()


def send_message(message):
    return bot.send_message(CHAT_ID, message)


def main():
    current_timestamp = int(time.time())

    while True:
        try:
            homeworks = get_homeworks(current_timestamp)
            message = parse_homework_status(homeworks)
            send_message(message)
            time.sleep(5 * 60)

        except Exception as e:
            print(f"Бот упал с ошибкой: {e}")
            time.sleep(5)


if __name__ == "__main__":
    main()
