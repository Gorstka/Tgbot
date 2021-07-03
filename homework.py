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
    homework_status = homework["status"]
    verdict = None
    if homework_status == "reviewing":
        verdict = "Работа взята на ревью."
    elif homework_status == "rejected":
        verdict = "К сожалению, в работе нашлись ошибки."
    else:
        verdict = "Ревьюеру всё понравилось, работа зачтена!"
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

    while True:
        try:
            homeworks = get_homeworks(0)
            if homeworks["homeworks"]:
                last_homework = homeworks["homeworks"][0]
                message = parse_homework_status(last_homework)
                send_message(message)
                time.sleep(480 * 60)

        except Exception as error:
            print(f"Бот упал с ошибкой: {error}")
            logging.error(error, exc_info=True)
            send_message(str(error))
            time.sleep(5)


if __name__ == "__main__":
    main()
