import click

from knn import utils
from knn.reducers import StatisticsReducer
from knn.jobs import MapReduceJob


@click.command()
@click.option("-m", "--mapper", type=str, required=True)
@click.option("-r", "--runtime", default=5)
@click.option("-c", "--num_cores", default=1)
@click.option("-n", "--num_trials", default=50)
@utils.unasync
async def main(mapper, runtime, num_cores, num_trials):
    job = MapReduceJob(
        mapper,
        StatisticsReducer(),
        {"runtime": runtime, "cores": num_cores},
        n_mappers=1000 if "run.app" in mapper else 1,
        n_retries=10,  # ensure we get all trials in
        chunk_size=1,  # hit different worker instances
    )
    stats = await job.run_until_complete([None] * num_trials)
    print(f"Mean: {stats.mean()}\nStd: {stats.stddev()}")


if __name__ == "__main__":
    main()
