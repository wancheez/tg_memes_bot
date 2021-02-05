from storage.postgres_storage import PGScheduler
import threading
import telebot
from memer import Memer
import os

TOKEN = os.environ['TG_TOKEN']
bot = telebot.TeleBot(TOKEN)
bot_scheduler = PGScheduler()


@bot.message_handler(commands=['wednesday'])
def schedule_wednesday(message):
    if message.chat:
        request_obj = {'chat_id': message.chat.id,
                       'type': 'wednesday'}
        bot_scheduler.update_scheduler(task_to_add=request_obj)
        bot.send_message(request_obj['chat_id'], "There will be Wednesday, my dudes!")
    else:
        bot.reply_to(message, f'Firstly, add bot to chat')


@bot.message_handler(commands=['memes'])
def schedule_memes(message):
    if message.chat:
        request_obj = {'chat_id': message.chat.id,
                       'type': 'memes'}
        bot_scheduler.update_scheduler(task_to_add=request_obj)
        bot.send_message(request_obj['chat_id'], "Get ready to memes")
    else:
        bot.reply_to(message, f'Firstly, add bot to chat')


def send_wednesday_to_chat(bot_to_run, chat_id):
    bot_to_run.send_message(chat_id, "It's Wednesday, my dudes!")
    bot_to_run.send_photo(chat_id, Memer.get_random_wendesday())


def send_memes(bot_to_run, chat_id):
    bot_to_run.send_photo(chat_id, Memer.get_random_meme())


@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, f'Hello, {message.from_user.first_name}.\n'
                          f'Add me to chat and send /wednesday @Wanbot to start reminding wednesdays\n'
                          f'Or send /memes @Wanbot to get memes everyday')


@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    if message.text.lower() in ('привет', 'hello', 'hi'):
        bot.send_message(message.from_user.id, 'Hello!')
    else:
        bot.send_message(message.from_user.id, 'Command ist recognised. Try to /help.')


def get_funcs_to_run():
    funcs = {
        'wednesday': send_wednesday_to_chat,
        'memes': send_memes,
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


if __name__ == "__main__":
    run_bot_threads()
