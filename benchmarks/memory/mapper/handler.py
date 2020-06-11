import asyncio
import os
from knn.mappers import Mapper


class BenchmarkMemoryMapper(Mapper):
    @staticmethod
    async def run_on_core(core):
        process = await asyncio.create_subprocess_shell(
            f"taskset -c {core} ./handler",
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
        )
        stdout, _ = await process.communicate()
        return float(stdout.decode())

    @Mapper.SkipIfError
    async def process_element(self, input, job_id, job_args, request_id, element_index):
        assert element_index == 0

        n_cores = job_args["cores"]
        assert n_cores <= os.cpu_count()

        # First select even cores, then select odd cores if necessary
        cores = []
        next_core = 0
        while n_cores > 0:
            cores.append(next_core)
            n_cores -= 1

            next_core += 2
            if next_core >= os.cpu_count():
                next_core = 1

        return sum(await asyncio.gather(*[self.run_on_core(core) for core in cores]))


mapper = BenchmarkMemoryMapper()
