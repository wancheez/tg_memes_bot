import json
import time

import schedule

SCHEDULER_FILE_DEFAULT = 'scheduler.json'


class BotScheduler:
    def __init__(self, scheduler_file=SCHEDULER_FILE_DEFAULT):
        self.scheduler_file = scheduler_file if scheduler_file else SCHEDULER_FILE_DEFAULT
        self.scheduler_runned = False

    def update_scheduler(self, task_to_add: dict):
        """
        Update scheduler file with new task
        :param task_to_add: data to add
        :return:
        """
        if not all(mand_key in task_to_add for mand_key in ('chat_id', 'type')):
            raise ValueError('Schedule type and chat id are mandatory')
        if task_to_add['type'].lower() == 'wednesday':
            updated_scheduler = self._add_scheduler(task_to_add, 'wednesday')
        if task_to_add['type'].lower() == 'memes':
            updated_scheduler = self._add_scheduler(task_to_add, 'memes')
        with open(self.scheduler_file, 'w') as f:
            json.dump(updated_scheduler, f)
            print('Scheduler file updated')

    def _get_scheduler(self):
        with open(self.scheduler_file, 'r') as f:
            scheduler_obj = json.load(f)
        return scheduler_obj

    def _add_scheduler(self, schedule_obj, schedule_name):
        scheduler = self._get_scheduler()
        if schedule_obj['chat_id'] in scheduler[schedule_name]:
            print(f'{schedule_name} scheduler already exists')
            return scheduler
        else:
            scheduler[schedule_name].append(schedule_obj['chat_id'])
            print(f'{schedule_name} scheduler added')
            return scheduler

    def run_scheduler(self, bot, wednesday_task=None, memes_task=None):
        self.scheduler_runned = False
        time.sleep(2)

        tasks = self._get_scheduler()
        for wednesday_chat_id in tasks['wednesday']:
            schedule.every().wednesday.at("09:30").do(wednesday_task, wednesday_chat_id)
            #schedule.every(5).seconds.do(wednesday_task, bot, wednesday_chat_id)
        for memes_chat_id in tasks['memes']:
            schedule.every().day.at("10:30").do(memes_task, bot, memes_chat_id)
            #schedule.every(5).seconds.do(memes_task, bot, memes_chat_id)
        print('Tasks scheduled')
        self.scheduler_runned = True
        while self.scheduler_runned:
            schedule.run_pending()
            time.sleep(1)
        print('Scheduler stopped')
