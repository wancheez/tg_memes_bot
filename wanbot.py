import asyncio
import datetime
import logging
import os
import random
from aiobalaboba import balaboba
from urllib.error import HTTPError

from aiogram import Bot, Dispatcher, exceptions, executor, types

from memer import Memer
from storage.base_storage import (schedule_meme_page, schedule_memes,
                                  schedule_wednesday)
from storage.postgres_storage import PGScheduler

TOKEN = os.environ['TG_TOKEN']
ADMIN_USER_ID = os.getenv('TG_ADMIN')
bot = Bot(TOKEN)
dp = Dispatcher(bot)
bot_scheduler = PGScheduler()
logging.basicConfig(level=logging.INFO)


@dp.message_handler(commands=['wednesday_now'])
async def schedule_wednesday_handler(message: types.Message):
    await send_wednesday_to_chat(bot, message.chat.id)


@dp.message_handler(commands=['subscribe_wednesday'])
async def schedule_wednesday_handler(message: types.Message):
    request_obj = _get_chat_info(message, 'wednesday')
    result_upd = bot_scheduler.update_scheduler(task_to_add=request_obj)
    if result_upd:
        schedule_wednesday(bot, get_funcs_to_run(), message.chat.id)
        await bot.send_message(request_obj['chat_id'], "There will be Wednesday, my dudes!")
    else:
        await bot.send_message(request_obj['chat_id'], "Already been set")


@dp.message_handler(commands=['unsubscribe_chat'])
async def unschedule_chat_handler(message):
    msg_text = message.text.replace('/unsubscribe_chat ', '')
    result_exec = unschedule_chat(msg_text)
    await message.reply(result_exec)


@dp.message_handler(commands=['memes'])
async def schedule_memes_handler(message):
    request_obj = _get_chat_info(message, 'memes')
    result_upd = bot_scheduler.update_scheduler(task_to_add=request_obj)
    if result_upd:
        schedule_memes(bot, get_funcs_to_run(), message.chat.id, subreddit=request_obj.get('arg', ''))
        await bot.send_message(request_obj['chat_id'], "Get ready to memes")
    else:
        await bot.send_message(request_obj['chat_id'], "Already been set")


@dp.message_handler(commands=['meme_page'])
async def schedule_meme_page_handler(message):
    request_obj = _get_chat_info(message, 'meme_page')
    result_upd = bot_scheduler.update_scheduler(task_to_add=request_obj)
    if result_upd:
        schedule_meme_page(bot, get_funcs_to_run(), message.chat.id, subreddit=request_obj.get('arg', ''))
        await bot.send_message(request_obj['chat_id'], "Now this is meme territory")
    else:
        await bot.send_message(request_obj['chat_id'], "Already been set")


@dp.message_handler(commands=['meme'])
async def send_meme_handler(message):
    subreddit = message.get_args()
    try:
        await send_memes(bot, message.chat.id, subreddit=subreddit)
    except ValueError as ex:
        await message.reply(ex)


@dp.message_handler(commands=['neuro_text'])
async def neuro_text_handler(message):
    memer = Memer()
    msg_text = message.text.replace('/neuro_text ', '')
    response = await memer.generate_text(msg_text)
    await message.reply(response)


@dp.message_handler(commands=['новый_год'])
async def new_year_handler(message):
    await message.reply('Временно не работает')
    return
    msg_text = message.text.replace('/новый_год ', '')
    response = await balaboba(msg_text, intro=20)
    response = response.replace(msg_text, '')
    if not response:
        await message.reply('Что-то пошло не так. Попробуй еще раз')
        return
    await message.reply(response)


@dp.message_handler(commands=['волк'])
async def wolf_handler(message):
    await message.reply('Временно не работает')
    return
    msg_text = message.text.replace('/волк ', '')
    response = await balaboba(msg_text, intro=3)
    if not response:
        await message.reply('Что-то пошло не так. Попробуй еще раз')
        return
    await message.reply(response)


@dp.message_handler(commands=['булава'])
async def neuro_text_handler(message):
    response = f'🍆У {message.from_user.first_name} булава {random.randint(1,50)} см 🍆'
    await message.reply(response)


async def send_wednesday_to_chat(bot_to_run, chat_id):
    await bot_to_run.send_message(chat_id, "Это среда, мои чуваки!")
    await bot_to_run.send_photo(chat_id, Memer().get_random_wednesday())


def unschedule_chat(chat_id):
    if not isinstance(chat_id, int):
        if not str.isdigit(chat_id):
            return 'Chat_id must be numeric'
        chat_id = int(chat_id)
    return bot_scheduler.delete_chat_id(chat_id)


async def send_memes(bot_to_run, chat_id, subreddit=''):
    success_sent = False
    count_tries = 0
    while not success_sent and count_tries < 5:
        try:
            meme, meme_ext = await Memer().get_random_meme(subreddit)
            if meme_ext.lower() == 'gif':
                await bot_to_run.send_document(chat_id, meme)
            else:
                await bot_to_run.send_photo(chat_id, meme)
            success_sent = True
        except exceptions.TelegramAPIError as exc:
            logging.error(f'API Error chat_id={chat_id}: {exc}')
            await inform_admin(f'API Error chat_id={chat_id}: {exc}')
            count_tries += 1
        except HTTPError as exc:
            logging.error(f'HTTP Error on chat_id={chat_id}: {exc}')
            await inform_admin(f'HTTP PError on chat_id={chat_id}: {exc}')


@dp.message_handler(commands=['start', 'help'])
async def send_welcome(message):
    await message.reply(f"""Hello, {message.from_user.first_name}.
/meme to get insta meme
/wednesday_now Wednesday today!
/schedule_wednesday reminding wednesdays
/memes to get one meme everyday
/meme_page memes every 2 hours
/neuro_text <text> продолжить текст
/булава 🍆
""")


async def inform_admin(text):
    if ADMIN_USER_ID:
        await bot.send_message(chat_id=ADMIN_USER_ID, text=text)


def get_funcs_to_run():
    funcs = {
        'wednesday': send_wednesday_to_chat,
        'memes': send_memes,
        'meme_page': send_memes,
    }
    return funcs


async def on_startup(_):
    bot_scheduler.run_scheduler(bot, get_funcs_to_run())
    asyncio.create_task(bot_scheduler.serve_scheduler())


def _get_chat_info(message, type_name):
    args = message.get_args()
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
        'subreddit': args if args else '',
    }


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)


