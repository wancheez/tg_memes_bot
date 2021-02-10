import json
import time
from abc import abstractmethod, ABC
import schedule

SCHEDULER_FILE_DEFAULT = 'scheduler.json'


class BaseScheduler(ABC):

    @abstractmethod
    def update_scheduler(self, task_to_add: dict):
        """
        Update scheduler file with new task
        :param task_to_add: data to add
        :return:
        """

    @abstractmethod
    def _get_scheduler(self):
        """
        Get all scheduled tasks
        :return:
        """

    def run_scheduler(self, bot, funcs):
        """
        Run all planned tasks
        :param bot:
        :param wednesday_task:
        :param memes_task:
        :return:
        """
        self.scheduler_runned = False
        time.sleep(2)

        tasks = self._get_scheduler()
        _run_scheduler_loop(bot, funcs, tasks)


def _run_scheduler_loop(bot, funcs, tasks):
    scheduler_runned = False
    time.sleep(2)
    for wednesday_chat_id in tasks['wednesday']:
        schedule_wednesday(bot, funcs, wednesday_chat_id)
        # schedule.every(5).seconds.do(funcs['wednesday'], bot, wednesday_chat_id)
    for memes_chat_id in tasks['memes']:
        schedule_memes(bot, funcs, memes_chat_id)
        # schedule.every(5).seconds.do(funcs['memes'], bot, memes_chat_id)
    for meme_page_chat_id in tasks['meme_page']:
        schedule_meme_page(bot, funcs, meme_page_chat_id)
    print('Tasks scheduled')
    scheduler_runned = True
    while scheduler_runned:
        schedule.run_pending()
        time.sleep(1)
    print('Scheduler stopped')


def schedule_meme_page(bot, funcs, chat_id):
    schedule.every(30).minutes.do(funcs['meme_page'], bot, chat_id)


def schedule_wednesday(bot, funcs, chat_id):
    schedule.every().wednesday.at("09:30").do(funcs['wednesday'], bot, chat_id)


def schedule_memes(bot, funcs, chat_id):
    schedule.every().day.at("10:30").do(funcs['memes'], bot, chat_id)
