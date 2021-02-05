import json
from storage.base_storage import BaseScheduler

SCHEDULER_FILE_DEFAULT = 'scheduler.json'


class JSONBotScheduler(BaseScheduler):
    def __init__(self, scheduler_file=SCHEDULER_FILE_DEFAULT):
        self.scheduler_file = scheduler_file if scheduler_file else SCHEDULER_FILE_DEFAULT
        self.scheduler_runned = False

    def update_scheduler(self, task_to_add: dict):
        """
        Update scheduler file with new task
        :param task_to_add: data to add
        :return:
        """
        updated_scheduler = None
        if not all(mand_key in task_to_add for mand_key in ('chat_id', 'type')):
            raise ValueError('Schedule type and chat id are mandatory')
        if task_to_add['type'].lower() == 'wednesday':
            updated_scheduler = self._add_scheduler(task_to_add, 'wednesday')
        if task_to_add['type'].lower() == 'memes':
            updated_scheduler = self._add_scheduler(task_to_add, 'memes')
        if not updated_scheduler:
            raise ValueError(f"Type {task_to_add['type']} is unrecognized")
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
