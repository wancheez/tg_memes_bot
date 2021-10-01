import datetime
import random

from storage.postgres_storage import PGScheduler
from storage.base_storage import schedule_meme_page, schedule_memes, schedule_wednesday
import threading
import telebot
from memer import Memer
from urllib.error import HTTPError
import os

TOKEN = os.environ['TG_TOKEN']
ADMIN_USER_ID = os.getenv('TG_ADMIN')
bot = telebot.TeleBot(TOKEN)
bot_scheduler = PGScheduler()


@bot.message_handler(commands=['wednesday'])
def schedule_wednesday_handler(message):
    request_obj = _get_chat_info(message, 'wednesday')
    result_upd = bot_scheduler.update_scheduler(task_to_add=request_obj)
    if result_upd:
        schedule_wednesday(bot, get_funcs_to_run(), message.chat.id)
        bot.send_message(request_obj['chat_id'], "There will be Wednesday, my dudes!")
    else:
        bot.send_message(request_obj['chat_id'], "Already been set")


@bot.message_handler(commands=['unsubscribe_chat'])
def unschedule_chat_handler(message):
    msg_text = message.text.replace('/unsubscribe_chat ', '')
    result_exec = unschedule_chat(msg_text)
    bot.reply_to(message, result_exec)


@bot.message_handler(commands=['memes'])
def schedule_memes_handler(message):
    request_obj = _get_chat_info(message, 'memes')
    result_upd = bot_scheduler.update_scheduler(task_to_add=request_obj)
    if result_upd:
        schedule_memes(bot, get_funcs_to_run(), message.chat.id)
        bot.send_message(request_obj['chat_id'], "Get ready to memes")
    else:
        bot.send_message(request_obj['chat_id'], "Already been set")


@bot.message_handler(commands=['meme_page'])
def schedule_meme_page_handler(message):
    request_obj = _get_chat_info(message, 'meme_page')
    result_upd = bot_scheduler.update_scheduler(task_to_add=request_obj)
    if result_upd:
        schedule_meme_page(bot, get_funcs_to_run(), message.chat.id)
        bot.send_message(request_obj['chat_id'], "Now this is meme territory")
    else:
        bot.send_message(request_obj['chat_id'], "Already been set")


@bot.message_handler(commands=['meme'])
def send_meme_handler(message):
    send_memes(bot, message.chat.id)


@bot.message_handler(commands=['neuro_text'])
def neuro_text_handler(message):
    memer = Memer()
    msg_text = message.text.replace('/neuro_text ', '')
    response = memer.generate_text(msg_text)
    bot.reply_to(message, response)


@bot.message_handler(commands=['булава'])
def neuro_text_handler(message):
    response = f'🍆У {message.from_user.first_name} булава {random.randint(1,50)} см 🍆'
    bot.reply_to(message, response)


def send_wednesday_to_chat(bot_to_run, chat_id):
    bot_to_run.send_message(chat_id, "It's Wednesday, my dudes!")
    bot_to_run.send_photo(chat_id, Memer.get_random_wednesday())


def unschedule_chat(chat_id):
    if not isinstance(chat_id, int):
        if not str.isdigit(chat_id):
            return 'Chat_id must be numeric'
        chat_id = int(chat_id)
    return bot_scheduler.delete_chat_id(chat_id)


def send_memes(bot_to_run, chat_id):
    success_sent = False
    count_tries = 0
    while not success_sent and count_tries < 5:
        try:
            meme, meme_ext = Memer.get_random_meme()
            if meme_ext.lower() == 'gif':
                bot_to_run.send_document(chat_id, meme)
            else:
                bot_to_run.send_photo(chat_id, meme)
            success_sent = True
        except telebot.apihelper.ApiTelegramException as exc:
            if exc.error_code == 403:
                result = unschedule_chat(chat_id)
                inform_admin(f'Unscheduling chat_id={chat_id}. Result: {result}')
            print(f'API Error chat_id={chat_id}: {exc}')
            inform_admin(f'API Error chat_id={chat_id}: {exc}')
            count_tries += 1
        except HTTPError as exc:
            print(f'HTTP Error on chat_id={chat_id}: {exc}')
            inform_admin(f'HTTP PError on chat_id={chat_id}: {exc}')


@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, f"""Hello, {message.from_user.first_name}.
/meme to get insta meme
/wednesday reminding wednesdays
/memes to get one meme everyday
/meme_page memes every 2 hours
/neuro_text <text> generate text with yandex neural networks
/булава 🍆""")


def inform_admin(text):
    if ADMIN_USER_ID:
        bot.send_message(chat_id=ADMIN_USER_ID, text=text)


def get_funcs_to_run():
    funcs = {
        'wednesday': send_wednesday_to_chat,
        'memes': send_memes,
        'meme_page': send_memes,
    }
    return funcs


def run_bot_threads(scheduler_thread=None, bot_thread=None):
    if scheduler_thread and scheduler_thread.is_alive():
        scheduler_thread.join()
    if bot_thread and bot_thread.is_alive():
        bot_thread.join()

    scheduler_thread = threading.Thread(target=bot_scheduler.run_scheduler,
                                        args=(bot, get_funcs_to_run()))
    bot_thread = threading.Thread(target=bot.polling, kwargs={'none_stop': True})
    scheduler_thread.start()
    bot_thread.start()


def _get_chat_info(message, type_name):
    if message.chat.title:
        title = message.chat.title
    else:
        title = f'Chat with {message.chat.username}'
    return {
        'chat_id': message.chat.id,
        'type': type_name,
        'chat_title': title,
        'created': datetime.datetime.now(),
        'creator': message.from_user.username,
    }


if __name__ == "__main__":
    run_bot_threads()
