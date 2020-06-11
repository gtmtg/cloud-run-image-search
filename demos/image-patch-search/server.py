import asyncio
import functools
from operator import itemgetter

from typing import Dict

from jinja2 import Environment, FileSystemLoader, select_autoescape
from sanic import Sanic
from sanic.response import json, html, text

from knn.jobs import MapReduceJob
from knn.reducers import TopKReducer, PoolingReducer
from knn.utils import FileListIterator, numpy_to_base64

import config


# Start web server
app = Sanic(__name__)
app.static("/static", "./static")
jinja = Environment(
    loader=FileSystemLoader("./templates"), autoescape=select_autoescape(["html"]),
)

current_queries = {}  # type: Dict[str, MapReduceJob]


@app.route("/")
async def homepage(request):
    template = jinja.get_template("index.html")
    response = template.render(
        n_concurrent_workers=config.N_CONCURRENT_WORKERS_DEFAULT,
        demo_images=config.DEMO_IMAGES,
        image_bucket=config.IMAGE_BUCKET,
    )
    return html(response)


@app.route("/start", methods=["POST"])
async def start(request):
    n_mappers = request.json["n_concurrent_workers"]

    # Get template
    template_job = MapReduceJob(
        config.TEMPLATE_ENDPOINT,
        PoolingReducer(PoolingReducer.PoolingType.AVG),
        {"input_bucket": config.IMAGE_BUCKET},
        n_mappers=n_mappers,
    )
    template_request = request.json["template"]
    template_result = await template_job.run_until_complete([template_request])
    template = numpy_to_base64(template_result)

    # Run query
    query_job = MapReduceJob(
        config.QUERY_ENDPOINT,
        TopKReducer(config.N_RESULTS_TO_DISPLAY, itemgetter("score")),
        {
            "input_bucket": config.IMAGE_BUCKET,
            "output_bucket": config.OUTPUT_BUCKET,
            "output_path": config.OUTPUT_PATH,
            "n_distances_to_average": config.N_DISTANCES_TO_AVERAGE,
            "template": template,
        },
        n_mappers=n_mappers,
        n_retries=1,
    )
    query_id = query_job.job_id
    current_queries[query_id] = query_job

    dataset = FileListIterator(config.IMAGE_LIST_PATH)
    cleanup_func = functools.partial(cleanup_query, query_id=query_id, dataset=dataset)
    await query_job.start(dataset, cleanup_func)

    return json({"query_id": query_id})


@app.route("/results", methods=["GET"])
async def get_results(request):
    query_id = request.args["query_id"][0]
    query_job = current_queries[query_id]
    if query_job.finished:
        current_queries.pop(query_id)

    results = query_job.job_result
    results["result"] = [r.to_dict() for r in results["result"]]  # make serializable
    return json(results)


@app.route("/stop", methods=["PUT"])
async def stop(request):
    query_id = request.json["query_id"]
    await current_queries.pop(query_id).stop()
    return text("", status=204)


def cleanup_query(_, query_id: str, dataset: FileListIterator):
    dataset.close()
    asyncio.create_task(final_query_cleanup(query_id))


async def final_query_cleanup(query_id: str):
    await asyncio.sleep(config.QUERY_CLEANUP_TIME)
    current_queries.pop(query_id, None)  # don't throw error if already deleted


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
