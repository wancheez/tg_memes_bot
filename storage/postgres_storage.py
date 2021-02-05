import os
import psycopg2
from storage.base_storage import BaseScheduler, _run_scheduler_loop

DB_NAME = os.environ['TG_DB_NAME']
DB_USERNAME = os.environ['TG_DB_USERNAME']
DB_PASSWORD = os.environ['TG_DB_PASSWORD']
DB_HOST = os.environ['TG_DB_HOST']


class PGScheduler(BaseScheduler):

    def __init__(self):
        self.conn = psycopg2.connect(dbname=DB_NAME, user=DB_USERNAME,
                                     password=DB_PASSWORD, host=DB_HOST)

    def update_scheduler(self, task_to_add: dict):
        """
        Update scheduler file with new task
        :param task_to_add: data to add
        :return:
        """
        if not all(mand_key in task_to_add for mand_key in ('chat_id', 'type')):
            raise ValueError('Schedule type and chat id are mandatory')
        with self.conn.cursor() as cursor:
            cursor.execute(f'SELECT * FROM schedule_tasks')
            tasks = [task for task in cursor]
        if task_to_add in tasks:
            return
        chat_id = task_to_add['chat_id']
        task_type_id = self._get_task_type_id_by_name(task_to_add['type'])
        with self.conn.cursor() as cursor:
            try:
                cursor.execute(f"INSERT INTO schedule_tasks VALUES ('{task_type_id}', {chat_id})")
                cursor.execute(f'commit')
                print(f'PG Storage updated with {task_to_add["type"]} to {chat_id}')
            except psycopg2.errors.UniqueViolation:
                print('Unique violation. Ignoring')
                cursor.execute('rollback')

    def _get_task_type_id_by_name(self, name):
        with self.conn.cursor() as cursor:
            cursor.execute(f"select task_type_id from schedule_types st where st.task_name='{name}'")
            type_id = [type_id for type_id in cursor]
        return type_id[0][0]

    def _get_scheduler(self):
        """
        Get all scheduled tasks
        :return:
        """
        tasks = None
        with self.conn.cursor() as cursor:
            cursor.execute(f"select st.chat_id, stp.task_name from schedule_tasks st, schedule_types stp "
                           "where st.task_type_id=stp.task_type_id")
            tasks_raw = [task for task in cursor]
            col_names = [desc[0] for desc in cursor.description]
            # map column_names with values
        tasks = [dict(zip(col_names, task)) for task in tasks_raw]
        return tasks

    def run_scheduler(self, bot, funcs):
        """
        Run all planned tasks
        :param bot:
        :param wednesday_task:
        :param memes_task:
        :return:
        """
        tasks = self._get_scheduler()
        prepared_tasks = dict()

        prepared_tasks['wednesday'] = (task['chat_id'] for task in tasks if task['task_name'] == 'wednesday')
        prepared_tasks['memes'] = (task['chat_id'] for task in tasks if task['task_name'] == 'memes')

        _run_scheduler_loop(bot, funcs, prepared_tasks)