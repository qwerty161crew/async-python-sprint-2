from job import GetRequestJob
from scheduler import Scheduler
import asyncio


async def main():
    job = GetRequestJob(
        data=['https://ya.ru/'])
    scheduler = Scheduler()

    scheduler.add_jobs(job)
    await scheduler.run()
    while True:
        await asyncio.sleep(0.1)
        if job.is_finished():
            await scheduler.save_all_job_state()
            # print(job.get_state())
            break


asyncio.run(main())
