import asyncio
import threading
from job import Job


class Scheduler:
    def __init__(self, pool_size=10):
        self.jobs: list[Job] = []
        self.pool_size = pool_size

    def add_jobs(self, *jobs):
        for job in jobs:
            self.jobs.append(job)

    def schedule(self, task):
        """запустить таску в указанное время"""
        pass

    async def run(self):
        """запустить задачи """
        run_coroutines = [job.start() for job in self.jobs]
        await asyncio.gather(*run_coroutines)

    async def restart(self):
        await self.stop()
        await self.run()

    async def pause(self):
        """поставить на паузу все задачи"""
        pause_coroutines = [job.pause() for job in self.jobs]
        await asyncio.gather(*pause_coroutines)

    async def stop(self):
        is_stop = None
        stop_coroutines = [job.stop() for job in self.jobs]
        await asyncio.gather(*stop_coroutines)

    def save_job_state(self, job: Job):
        with open(f'{job.identifier}.txt', 'w') as file:
            file.write(job.get_state())

    async def save_all_job_state(self, jobs):
        while True:
            await asyncio.sleep(1)
            if self.all_jobs_finished():
                break
            for job in jobs:
                self.save_job_state(job)

    def all_jobs_finished(self):
        for job in self.jobs:
            if job.is_finished() is False:
                return False
        return True
