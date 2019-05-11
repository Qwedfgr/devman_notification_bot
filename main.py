import requests
import telegram
import time
import os
import logging
import log_utils
import dotenv


def main():
    dotenv.load_dotenv()
    token = os.environ["token"]
    chat_id = os.environ["chat_id"]
    devman_token = os.environ["devman_token"]
    token_logger = os.environ['token_log']

    logger_bot = telegram.Bot(token=token_logger)
    logger = logging.getLogger("bot-logger")
    logger.setLevel(logging.INFO)
    logger.addHandler(log_utils.MyLogsHandler(logger_bot, chat_id))
    logger.info("Бот логер запущен!")

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
            bot = telegram.Bot(token=token)
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            response_data = response.json()
            if response_data['status'] == 'found':
                params['timestamp'] = response_data['last_attempt_timestamp']
                send_messages(bot, response_data['new_attempts'], chat_id)
            else:
                params['timestamp'] = response_data['timestamp_to_request']
        except (requests.exceptions.ConnectionError, requests.exceptions.ReadTimeout) as error:
            logger.error('Ошибка соединения:')
            logger.error(error)
            time.sleep(30)
        except requests.exceptions.HTTPError as error:
            logger.error(error)
            break
        except Exception as error:
            logger.error('Бот упал с ошибкой:')
            logger.error(error)
            break


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

