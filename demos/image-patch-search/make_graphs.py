import click
from click_option_group import optgroup, RequiredMutuallyExclusiveOptionGroup
import collections
import json


@click.command()
@click.argument("input", type=click.File("r"))
@optgroup.group(
    "Graph types", cls=RequiredMutuallyExclusiveOptionGroup,
)
@optgroup.option("-b", "--breakdown", is_flag=True)
@optgroup.option("-t", "--throughput", is_flag=True)
@optgroup.option("-w", "--workers", is_flag=True)
def main(input, breakdown, throughput, workers):
    results = json.load(input)

    if breakdown:
        times = results[-1]["performance"]["profiling"]
        if "boot_time" in times:
            print(times["boot_time"])
            print(len(results[-1]["performance"]["mapper_utilization"]))
            print()
        print(times["total_time"] - times["billed_time"])  # Cloud Run overhead
        print(times["billed_time"] - times["request_time"])  # Model loading
        print(times["request_time"] - times["compute_time"])  # I/O
        print(times["compute_time"])  # Compute
    elif throughput:
        prev_progress = {}
        for result in results:
            progress = result["progress"]
            dn = progress["n_processed"] - prev_progress.get("n_processed", 0)
            dt = progress["elapsed_time"] - prev_progress.get("elapsed_time", 0)
            print(dn / dt)
            prev_progress = progress
    elif workers:
        chunks_per_worker = results[-1]["performance"]["mapper_utilization"]

        histogram_data = collections.defaultdict(int)
        n_max = 0
        for n in chunks_per_worker.values():
            histogram_data[n] += 1
            n_max = max(n_max, n)

        for i in range(1, n_max):
            print(histogram_data[i])


if __name__ == "__main__":
    main()
