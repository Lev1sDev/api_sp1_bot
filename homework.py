import logging
import os
import time

import requests
import telegram
from dotenv import load_dotenv

load_dotenv()

PRAKTIKUM_TOKEN = os.getenv("PRAKTIKUM_TOKEN")
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
URL = 'https://praktikum.yandex.ru/api/user_api/homework_statuses/'


def parse_homework_status(homework):
    homework_name = homework.get('homework_name')
    if homework.get('status') == 'rejected':
        verdict = 'К сожалению в работе нашлись ошибки.'
    else:
        verdict = (
            'Ревьюеру всё понравилось, можно приступать к следующему уроку.'
        )
    return f'У вас проверили работу "{homework_name}"!\n\n{verdict}'


def get_homework_statuses(current_timestamp):
    headers = {'Authorization': f'OAuth {PRAKTIKUM_TOKEN}'}
    if current_timestamp is None:
        current_timestamp = int(time.time())
    params = {'from_date': current_timestamp}
    try:  # pytest не позволяет использовать метод raise_for_status()
        homework_statuses = requests.get(URL, headers=headers, params=params)
        return homework_statuses.json()
    except requests.RequestException as error:
        return logging.error(error, exc_info=True)


def send_message(message, bot_client):
    return bot_client.send_message(chat_id=CHAT_ID, text=message)


def main():
    bot_client = telegram.Bot(token=TELEGRAM_TOKEN)
    logging.basicConfig(level=logging.DEBUG)
    logging.debug('Запуск бота-ассистента')
    current_timestamp = int(time.time())

    while True:
        try:
            new_homework = get_homework_statuses(current_timestamp)
            if new_homework.get('homeworks'):
                send_message(
                    parse_homework_status(new_homework.get('homeworks')[0]),
                    bot_client
                )
                logging.info('Сообщение отправлено')
            current_timestamp = new_homework.get(
                'current_date', current_timestamp
            )
            time.sleep(300)

        except Exception as e:
            logging.error(f'Бот столкнулся с ошибкой: {e}')
            send_message('Бот столкнулся с ошибкой', bot_client)
            time.sleep(5)
            # не совсем понял зачем выбрасывать ошибку каждые 5 секунд


if __name__ == '__main__':
    main()
