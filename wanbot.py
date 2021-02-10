from storage.postgres_storage import PGScheduler
from storage.base_storage import schedule_meme_page, schedule_memes, schedule_wednesday
import threading
import telebot
from memer import Memer
import os

TOKEN = os.environ['TG_TOKEN']
bot = telebot.TeleBot(TOKEN)
bot_scheduler = PGScheduler()


@bot.message_handler(commands=['wednesday'])
def schedule_wednesday_handler(message):
    request_obj = {'chat_id': message.chat.id,
                   'type': 'wednesday'}
    result_upd = bot_scheduler.update_scheduler(task_to_add=request_obj)
    if result_upd:
        schedule_wednesday(bot, get_funcs_to_run(), message.chat.id)
        bot.send_message(request_obj['chat_id'], "There will be Wednesday, my dudes!")
    else:
        bot.send_message(request_obj['chat_id'], "Already been set")


@bot.message_handler(commands=['memes'])
def schedule_memes_handler(message):
    request_obj = {'chat_id': message.chat.id,
                   'type': 'memes'}
    result_upd = bot_scheduler.update_scheduler(task_to_add=request_obj)
    if result_upd:
        schedule_memes(bot, get_funcs_to_run(), message.chat.id)
        bot.send_message(request_obj['chat_id'], "Get ready to memes")
    else:
        bot.send_message(request_obj['chat_id'], "Already been set")


@bot.message_handler(commands=['meme_page'])
def schedule_meme_page_handler(message):
    request_obj = {'chat_id': message.chat.id,
                   'type': 'meme_page'}
    result_upd = bot_scheduler.update_scheduler(task_to_add=request_obj)
    if result_upd:
        schedule_meme_page(bot, get_funcs_to_run(), message.chat.id)
        bot.send_message(request_obj['chat_id'], "Now this is meme territory")
    else:
        bot.send_message(request_obj['chat_id'], "Already been set")


@bot.message_handler(commands=['meme'])
def send_meme_handler(message):
    bot.send_photo(message.chat.id, Memer.get_random_meme())


def send_wednesday_to_chat(bot_to_run, chat_id):
    bot_to_run.send_message(chat_id, "It's Wednesday, my dudes!")
    bot_to_run.send_photo(chat_id, Memer.get_random_wendesday())


def send_memes(bot_to_run, chat_id):
    bot_to_run.send_photo(chat_id, Memer.get_random_meme())


@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, f'Hello, {message.from_user.first_name}.\n'
                          f'Send /meme to get insta meme\n'
                          f'Add me to chat and send /wednesday to start reminding wednesdays\n'
                          f'Or send /memes to get one meme everyday\n')


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


if __name__ == "__main__":
    run_bot_threads()

