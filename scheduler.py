import asyncio
from datetime import datetime
from job import Job


class Scheduler:
    def __init__(self, pool_size=10):
        self.jobs: list[Job] = []
        self.pool_size = pool_size
        self.task_save = None

    def add_jobs(self, *jobs):
        for job in jobs:
            self.jobs.append(job)

    async def _schedule(self, job, time):
        """запустить таску в указанное время"""
        await asyncio.sleep((datetime.now() - time).total_seconds())
        await job.start()

    async def shedule(self, job: Job, time: datetime):
        """запустить таску в указанное время"""
        if job in self.jobs:
            raise ValueError('Вы уже добавили это задания!')
        self.jobs.append(job)
        await asyncio.create_task(self._schedule(job, time))

    async def run(self):
        """запустить задачи """
        run_coroutines = [job.start() for job in self.jobs]
        await asyncio.gather(*run_coroutines)
        self.task_save = await asyncio.create_task(self.save_all_job_state())

    async def restart(self):
        await self.stop()
        await self.run()

    async def pause(self):
        """поставить на паузу все задачи"""
        pause_coroutines = [job.pause() for job in self.jobs]
        await asyncio.gather(*pause_coroutines)

    async def stop(self):
        stop_coroutines = [job.stop() for job in self.jobs]
        await asyncio.gather(*stop_coroutines)
        self.task_save.cancel()

    def save_job_state(self, job: Job):
        with open(f'{job.identifier}.txt', 'w') as file:
            file.write(job.get_state())

    async def save_all_job_state(self):
        while True:
            await asyncio.sleep(1)
            for job in self.jobs:
                self.save_job_state(job)
            if self.all_jobs_finished():
                break

    def all_jobs_finished(self):
        for job in self.jobs:
            if job.is_finished() is False:
                return False
        return True
