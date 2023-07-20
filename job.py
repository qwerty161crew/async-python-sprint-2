import aiohttp

import json
import asyncio
import datetime
import time
import uuid
from typing import Optional


class Job:
    def __init__(self, start_at: datetime.datetime = None, max_working_time=-1,
                 tries=0, dependencies=None, data=None, state=None):
        self.dependencies = dependencies or []
        self.start_at = start_at
        self.data = data
        self.task = None
        self.set_state(state)
        self._uuid = uuid.uuid4()

    def get_state(self, *args, **kwargs):
        pass
        # raise NotImplemented

    async def start(self):
        if self.start_at:
            await asyncio.create_task(self._start_at_time(self.start_at))
        else:
            await self._start()

    async def _start(self):
        while True:
            if self._dependencies_are_finished():
                break
            asyncio.sleep(0.1)

        self.start_time = time.time()
        self.task = await asyncio.create_task(self._run())

    async def _dependencies_are_finished(self):
        return all(job.is_finished() for job in self.dependencies)

    async def _start_at_time(self, time: datetime):
        await asyncio.sleep((datetime.now() - time).total_seconds())
        await self._start()

    def set_state(self, state: str) -> None:
        pass
        # raise NotImplemented

    async def pause(self):
        pass
        # raise NotImplemented

    async def stop(self):
        pass
        # raise NotImplemented

    @property
    def identifier(self) -> str:
        """возвращает уникальный индификатор jobs"""
        return self._uuid


class GetRequestJob(Job):
    """принимает список ссылок и делает get запросы"""
    state: dict[dict[str, Optional[str]]]

    def __init__(self, start_at: datetime = None,
                 max_working_time=datetime.timedelta(
            minutes=1), tries=0, dependencies=None,
            data: list[str] = None, state=None):
        """ 
        data - список ссылок
        state - статусы работа
        """
        super().__init__(start_at, max_working_time, tries, dependencies, data)
        self.max_working_time = max_working_time

    async def _make_request(self, url) -> str:  # tudo получить строку
        async with aiohttp.ClientSession() as session:
            if self.start_time >= 60:
                try:
                    result = await session.get(url)
                    result_text = await result.text()
                except Exception as error:
                    self.state[url] = dict(result=None, error=str(error))
                else:
                    self.state[url] = dict(result=result_text, error=None)
        return result_text

    def is_finished(self) -> bool:
        return len(self.state) == len(self.data)

    async def _run(self):
        for url in self.data:
            if (datetime.timedelta(time.time()
                                   - self.start_time)
                    >= self.max_working_time):
                return
            if url not in self.state:
                response = await self._make_request(url)
                self.state[url] = response

    def get_state(self, *args, **kwargs):
        return json.dumps(self.state)

    def set_state(self, state: str):
        if state is None:
            self.state = {}
        else:
            self.state = json.loads(state)
