import requests
import telegram
import time
import os
from dotenv import load_dotenv


def main():
    load_dotenv()
    token = os.getenv("token")
    chat_id = os.getenv("chat_id")
    devman_token = os.getenv("devman_token")
    bot = telegram.Bot(token=token)
    url = 'https://dvmn.org/api/long_polling/'
    headers = {
        'Authorization': devman_token
    }
    timestamp = time.time()
    params = {
        'timestamp': timestamp
    }
    while True:
        try:
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            response_data = response.json()
            if response_data['status'] == 'found':
                params['timestamp'] = response_data['last_attempt_timestamp']
                send_messages(bot, response_data['new_attempts'], chat_id)
            else:
                params['timestamp'] = response_data['timestamp_to_request']
        except (requests.exceptions.ConnectionError, requests.exceptions.ReadTimeout) as error:
            time.sleep(30)


def send_messages(bot, attempts, chat_id):
    for attempt in attempts:
        if attempt['is_negative']:
            message = """У вас проверили работу "{}". К сожалению в работе нашлись ошибки.""".format(
                attempt['lesson_title'])
        else:
            message = """У вас проверили работу "{}". Преподавателю все понравилось, можно приступать к следующему уроку!""".format(
                attempt['lesson_title'])
        bot.sendMessage(chat_id=chat_id, text=message)


if __name__ == '__main__':
    main()

