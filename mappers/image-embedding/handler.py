import math

import torch

from knn import utils
from knn.mappers import Mapper

from base import ResNetBackboneMapper
import config


class ImageEmbeddingMapper(ResNetBackboneMapper):
    @Mapper.SkipIfError
    async def process_element(self, input, job_id, job_args, request_id, element_index):
        image_bucket = job_args["input_bucket"]
        image_path = input["image"]
        x1, y1, x2, y2 = input.get("patch", (0, 0, 1, 1))

        spatial_embeddings = await self.download_and_process_image(
            image_bucket, image_path, request_id
        )

        with self.profiler(request_id, "compute_time"):
            _, h, w = spatial_embeddings.size()

            x1 = int(math.floor(x1 * w))
            y1 = int(math.floor(y1 * h))
            x2 = int(math.ceil(x2 * w))
            y2 = int(math.ceil(y2 * h))

            embedding = spatial_embeddings[:, y1:y2, x1:x2].mean(dim=-1).mean(dim=-1)
            embedding = torch.nn.functional.normalize(embedding, p=2, dim=0)

        return utils.numpy_to_base64(embedding.numpy())


mapper = ImageEmbeddingMapper(
    config.RESNET_CONFIG, config.WEIGHTS_CLOUD_PATH, config.WEIGHTS_LOCAL_PATH,
)
