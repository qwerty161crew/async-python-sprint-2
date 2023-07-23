import asyncio
from datetime import datetime
from job import Job
from os import listdir


class Scheduler:
    DIRECTORIA = 'file_job/'

    def __init__(self, pool_size=10):
        """мне полностью проект переделывать ?
        обязательно использовать yield и удалить async?"""
        self.jobs: list[Job] = []
        self.pool_size = pool_size
        self.task_save = None

    def add_jobs(self, *jobs):
        for job in jobs:
            self.jobs.append(job)

    async def _schedule(self, job, time) -> None:
        """запустить таску в указанное время"""
        await asyncio.sleep((datetime.now() - time).total_seconds())
        await job.start()

    async def schedule(self, job: Job, time: datetime) -> None:
        """запустить таску в указанное время"""
        if job in self.jobs:
            raise ValueError('Вы уже добавили это задания!')
        self.jobs.append(job)
        await asyncio.create_task(self._schedule(job, time))

    async def _read_file(self, filename) -> None:
        with open(f'{self.DIRECTORIA}{filename}.txt', 'r') as file:
            print(file, file.read())

    async def reads_files(self) -> None:
        onlyfiles = [f for f in listdir(
            self.DIRECTORIA) if f.endswith('.txt')]
        for file in onlyfiles:
            await self._read_file(f'{self.DIRECTORIA}{file}')

    async def run(self) -> None:
        """запустить задачи """
        run_coroutines = [job.start() for job in self.jobs]
        await asyncio.gather(*run_coroutines)
        self.task_save = await asyncio.create_task(self.save_all_job_state())

    async def restart(self) -> None:
        await self.stop()
        await self.run()

    async def pause(self) -> None:
        """поставить на паузу все задачи"""
        pause_coroutines = [job.pause() for job in self.jobs]
        await asyncio.gather(*pause_coroutines)

    async def stop(self) -> None:
        stop_coroutines = [job.stop() for job in self.jobs]
        await asyncio.gather(*stop_coroutines)
        self.task_save.cancel()

    def save_job_state(self, job: Job) -> None:
        with open(f'{self.DIRECTORIA}{job.identifier()}.txt', 'w') as file:
            file.write(job.get_state())

    async def save_all_job_state(self) -> None:
        while True:
            await asyncio.sleep(1)
            for job in self.jobs:
                self.save_job_state(job)
            if self.all_jobs_finished():
                break

    def all_jobs_finished(self) -> bool:
        for job in self.jobs:
            if job.is_finished() is False:
                return False
        return True
