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
        time.sleep(2)

        tasks = self._get_scheduler()
        self._run_scheduler_loop(bot, funcs, tasks)


    def _run_scheduler_loop(self, bot, funcs, tasks):
        time.sleep(2)
        for wednesday_chat_id in tasks['wednesday']:
            schedule_wednesday(bot, funcs, wednesday_chat_id)
        for memes_chat_id in tasks['memes']:
            schedule_memes(bot, funcs, memes_chat_id)
        for meme_page_chat_id in tasks['meme_page']:
            schedule_meme_page(bot, funcs, meme_page_chat_id)
        print('Tasks scheduled')
        while True:
            schedule.run_pending()
            time.sleep(1)


def schedule_meme_page(bot, funcs, chat_id):
    schedule.every(2).hours.do(funcs['meme_page'], bot, chat_id)


def schedule_wednesday(bot, funcs, chat_id):
    schedule.every().wednesday.at("10:00").do(funcs['wednesday'], bot, chat_id)


def schedule_memes(bot, funcs, chat_id):
    # Exclude wednesday
    schedule.every().sunday.at("11:30").do(funcs['memes'], bot, chat_id)
    schedule.every().monday.at("11:30").do(funcs['memes'], bot, chat_id)
    schedule.every().tuesday.at("11:30").do(funcs['memes'], bot, chat_id)
    schedule.every().thursday.at("11:30").do(funcs['memes'], bot, chat_id)
    schedule.every().friday.at("11:30").do(funcs['memes'], bot, chat_id)
    schedule.every().saturday.at("11:30").do(funcs['memes'], bot, chat_id)

