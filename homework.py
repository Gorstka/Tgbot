import logging
import os
import time
from http import HTTPStatus

import requests
import telegram
from dotenv import load_dotenv

load_dotenv()


PRAKTIKUM_TOKEN = os.getenv("PRAKTIKUM_TOKEN")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
url = "https://praktikum.yandex.ru/api/user_api/homework_statuses/"

bot = telegram.Bot(token=TELEGRAM_TOKEN)


logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s, %(levelname)s, %(name)s, %(message)s",
    filename="main.log",
    filemode="w",
)


class TGBotException(Exception):
    pass


def parse_homework_status(homework):

    if "homework_name" not in homework or "status" not in homework:
        raise TGBotException(
            "Работа не содержит обязательные поля - status и homework_name"
        )
    homework_name = homework["homework_name"]
    homework_status = homework["status"]
    if homework_status == "reviewing":
        verdict = "Работа взята на ревью."
    elif homework_status == "rejected":
        verdict = "К сожалению, в работе нашлись ошибки."
    elif homework_status == "approved":
        verdict = "Ревьюеру всё понравилось, работа зачтена!"
    else:
        raise TGBotException("Работа содержит иной status")
    return f'У вас проверили работу "{homework_name}"!\n\n{verdict}'


def get_homeworks(current_timestamp):
    headers = {"Authorization": f"OAuth {PRAKTIKUM_TOKEN}"}
    payload = {"from_date": current_timestamp}
    try:
        homework_statuses = requests.get(url, headers=headers, params=payload)
    except requests.exceptions.RequestException as err:
        raise TGBotException(f"Не удалось выполнить запрос к серверу - {err}")
    if homework_statuses.status_code != HTTPStatus.OK:
        raise TGBotException(
            "Сервер вернул ответ с некорректным статусом -"
            f"{homework_statuses.status_code}"
        )
    return homework_statuses.json()


def send_message(message):
    return bot.send_message(CHAT_ID, message)


def main():
    current_timestamp = int(time.time())

    while True:
        try:
            homeworks = get_homeworks(current_timestamp)
            print(homeworks)
            if homeworks["homeworks"]:
                last_homework = homeworks["homeworks"][0]
                message = parse_homework_status(last_homework)
                send_message(message)
            time.sleep(5 * 60)

        except Exception as error:
            logging.error(error, exc_info=True)
            send_message(str(error))
            time.sleep(5)


if __name__ == "__main__":
    main()
