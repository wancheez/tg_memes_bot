import os
import time
import aioschedule
import asyncio

import psycopg2
import threading
from storage.base_storage import BaseScheduler, schedule_meme_page, schedule_memes, schedule_wednesday


DB_NAME = os.environ['TG_DB_NAME']
DB_USERNAME = os.environ['TG_DB_USERNAME']
DB_PASSWORD = os.environ['TG_DB_PASSWORD']
DB_HOST = os.environ['TG_DB_HOST']


class PGScheduler(BaseScheduler):

    def __init__(self):
        self.conn = psycopg2.connect(dbname=DB_NAME, user=DB_USERNAME,
                                     password=DB_PASSWORD, host=DB_HOST)
        self.stop_event = threading.Event()
        self.bot = None
        self.funcs = None

    def update_scheduler(self, task_to_add: dict):
        """
        Update scheduler file with new task
        :param task_to_add: data to add
        :return:
        """
        if not all(mand_key in task_to_add for mand_key in ('chat_id', 'type')):
            raise ValueError('Schedule type and chat id are mandatory')
        with self.conn.cursor() as cursor:
            cursor.execute(f'SELECT * FROM meme_schedules_scheduletask')
            tasks = [task for task in cursor]
        if task_to_add in tasks:
            print(f'Chat already added')
            return
        chat_id = task_to_add['chat_id']
        task_to_add['task_type_id'] = self._get_task_type_id_by_name(task_to_add['type'])

        with self.conn.cursor() as cursor:
            try:
                cursor.execute("""
                    INSERT INTO meme_schedules_scheduletask (chat_id, task_type_id, chat_title, created, creator)
                    VALUES (%(chat_id)s, %(task_type_id)s, %(chat_title)s, %(created)s, %(creator)s)
                    """,
                    task_to_add,
                )
                cursor.execute('commit')
                print(f'PG Storage updated with {task_to_add["type"]} to {chat_id}')
            except psycopg2.errors.UniqueViolation:
                print('Unique violation. Ignoring')
                cursor.execute('rollback')
                return False
        return True

    def delete_chat_id(self, chat_id: int):
        schedules = self._get_scheduler()
        if chat_id not in [schedule['chat_id'] for schedule in schedules]:
            return f'No such schedule with chat_id={chat_id}'
        with self.conn.cursor() as cursor:
            query = f'DELETE FROM meme_schedules_scheduletask WHERE chat_id=%(chat_id)s'
            cursor.execute(
                query,
                {'chat_id': chat_id}
            )
            self.conn.commit()
        self.restart_scheduler()

        return f'Scheduling with chat_id={chat_id} deleted'

    def restart_scheduler(self):
        """Restart scheduler

        :return:
        """
        self.stop_event.set()
        print(f'Scheduler stopping')
        time.sleep(5)
        self.stop_event.clear()
        schedule_thread = threading.Thread(
            target=self.run_scheduler,
            args=(self.bot, self.funcs),
            daemon=True,
        )
        time.sleep(5)
        schedule_thread.start()

    def _get_task_type_id_by_name(self, name):
        with self.conn.cursor() as cursor:
            cursor.execute(f"select task_type_id from meme_schedules_tasktype st where st.task_name='{name}'")
            type_id = [type_id for type_id in cursor]
        return type_id[0][0]

    def _get_scheduler(self):
        """
        Get all scheduled tasks
        :return:
        """
        with self.conn.cursor() as cursor:
            cursor.execute(f"""select st.chat_id, stp.name as task_name
                           from meme_schedules_scheduletask st, meme_schedules_tasktype stp 
                           where st.task_type_id=stp.id""")
            tasks_raw = [task for task in cursor]
            col_names = [desc[0] for desc in cursor.description]
            # map column_names with values
        tasks = [dict(zip(col_names, task)) for task in tasks_raw]
        return tasks

    def run_scheduler(self, bot, funcs):
        """
        Run all planned tasks
        :param funcs:
        :param bot:

        :return:
        """
        tasks = self._get_scheduler()
        prepared_tasks = dict()
        self.bot = bot
        self.funcs = funcs

        prepared_tasks['wednesday'] = (task['chat_id'] for task in tasks if task['task_name'] == 'wednesday')
        prepared_tasks['memes'] = (task['chat_id'] for task in tasks if task['task_name'] == 'memes')
        prepared_tasks['meme_page'] = (task['chat_id'] for task in tasks if task['task_name'] == 'meme_page')

        self._run_scheduler_loop(bot, funcs, prepared_tasks)

    def _run_scheduler_loop(self, bot, funcs, tasks):

        time.sleep(2)
        for wednesday_chat_id in tasks['wednesday']:
            schedule_wednesday(bot, funcs, wednesday_chat_id)
        for memes_chat_id in tasks['memes']:
            schedule_memes(bot, funcs, memes_chat_id)
        for meme_page_chat_id in tasks['meme_page']:
            schedule_meme_page(bot, funcs, meme_page_chat_id)
        print('Tasks scheduled')
        while not self.stop_event.is_set():
            await aioschedule.run_pending()
            time.sleep(1)

        print('Scheduler stopped')
