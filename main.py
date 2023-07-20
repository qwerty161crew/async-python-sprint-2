from job import GetRequestJob
from scheduler import Scheduler
import asyncio


async def main():
    job = GetRequestJob(
        data=['https://docs.python.org/3/library/datetime.html'])
    scheduler = Scheduler()
    
    scheduler.add_jobs(job)
    await scheduler.run()
    while True:
        await asyncio.sleep(0.1)
        if job.is_finished():
            await scheduler.save_all_job_state()
            print(job.get_state())
            break


asyncio.run(main())
