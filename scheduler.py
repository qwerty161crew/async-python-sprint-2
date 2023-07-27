import logging
from typing import Optional

import logger
from job import Job

logger = logging.getLogger(__name__)


class Scheduler:
    def __init__(self, pool_size: int = 10):
        self.queue: list = []
        self.pool_size = pool_size
        self.job_to_do = Job.run()

    def add_task(self, tasks: list[Job]) -> None:
        length: int = len(tasks)
        logger.info('Tasks gotten: %(length)s', {'length': length})
        if length > self.pool_size:
            for task in tasks[:self.pool_size]:
                self.queue.append(task)
        else:
            for task in tasks:
                self.queue.append(task)

    def get_task(self) -> Optional[Job]:
        if not self.queue:
            logger.info('Empty queue')
            return None
        task: Job = self.queue.pop(0)
        logger.info('Got task from queue')
        return task

    def run(self) -> None:
        while True:
            task: Optional[Job] = self.get_task()
            if not task:
                break
            self.job_to_do.send((
                task.func,
                task.tries,
                task.start_at,
                task.max_working_time,
            ))