import abc
import asyncio
import collections
from dataclasses import dataclass
import functools
import json
import time
import uuid

from typing import Dict, Any, DefaultDict

import sanic

from knn.utils import JSONType


@dataclass
class RequestProfiler:
    request_id: str
    category: str
    results_dict: Dict[str, DefaultDict[str, float]]
    additional: float = 0.0

    def __enter__(self):
        self.start_time = time.time()

    def __exit__(self, type, value, traceback):
        self.results_dict[self.request_id][self.category] += (
            time.time() - self.start_time + self.additional
        )


class Mapper(abc.ABC):
    # BASE CLASS

    def initialize_container(self, *args, **kwargs) -> None:
        pass

    async def initialize_job(self, job_args: JSONType) -> Any:
        return job_args

    @abc.abstractmethod
    async def process_element(
        self,
        input: JSONType,
        job_id: str,
        job_args: Any,
        request_id: str,
        element_index: int,
    ) -> JSONType:
        pass

    # DECORATORS

    @staticmethod
    def SkipIfAssertionError(f):
        @functools.wraps(f)
        async def wrapper(*args, **kwargs):
            try:
                return await f(*args, **kwargs)
            except AssertionError:
                pass
            return None

        return wrapper

    @staticmethod
    def SkipIfError(f):
        @functools.wraps(f)
        async def wrapper(*args, **kwargs):
            try:
                return await f(*args, **kwargs)
            except Exception:
                pass
            return None

        return wrapper

    # INTERNAL

    def __init__(self, *args, start_server=True, **kwargs):
        self._init_start_time = time.time()

        self.worker_id = str(uuid.uuid4())
        self._args_by_job: Dict[str, Any] = {}
        self._profiling_results_by_request: DefaultDict[
            str, DefaultDict[str, float]
        ] = collections.defaultdict(lambda: collections.defaultdict(float))
        self.profiler = functools.partial(
            RequestProfiler, results_dict=self._profiling_results_by_request
        )

        self.initialize_container(*args, **kwargs)

        if start_server:
            self._server = sanic.Sanic(self.worker_id)
            self._server.add_route(self._handle_request, "/", methods=["POST"])
            self._server.add_route(self._sleep, "/sleep", methods=["POST"])
        else:
            self._server = None

        self._init_time = time.time() - self._init_start_time
        self._boot_time = None  # will be set later

    async def __call__(self, *args, **kwargs):
        if self._server is not None:
            return await self._server(*args, **kwargs)

    async def _process_element_enumerated(
        self,
        input: JSONType,
        job_id: str,
        job_args: Any,
        request_id: str,
        element_index: int,
    ):
        return (
            element_index,
            await self.process_element(
                input, job_id, job_args, request_id, element_index
            ),
        )

    async def _handle_request(self, request):
        request_id = str(uuid.uuid4())
        job_id = request.json["job_id"]
        job_args = self._args_by_job.setdefault(
            job_id, await self.initialize_job(request.json["job_args"])
        )  # memoized

        async def process_chunk_streaming(response):
            for coro in asyncio.as_completed(
                [
                    self._process_element_enumerated(
                        input, job_id, job_args, request_id, i
                    )
                    for i, input in enumerate(request.json["inputs"])
                ]
            ):
                i, output = await coro
                await response.write(
                    json.dumps(
                        {"worker_id": self.worker_id, "index": i, "output": output}
                    )
                )

        return sanic.response.stream(process_chunk_streaming)

    async def _sleep(self, request):
        delay = float(request.json["delay"])
        await asyncio.sleep(delay)
        return sanic.response.json(request.json)
