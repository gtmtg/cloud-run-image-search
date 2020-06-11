import base64
import io

from google.cloud import storage
import numpy as np
from PIL import Image
import torch

from detectron2 import model_zoo
from detectron2.config import get_cfg
from detectron2.data import MetadataCatalog
from detectron2.engine.defaults import DefaultPredictor
from detectron2.utils.visualizer import Visualizer

from knn.mappers import Mapper


MODEL = "COCO-InstanceSegmentation/mask_rcnn_R_50_FPN_3x.yaml"
WEIGHTS_PATH = "model_final_f10217.pkl"


class SegmentationMapper(Mapper):
    def initialize_container(self):
        cfg = get_cfg()
        cfg.merge_from_file(model_zoo.get_config_file(MODEL))
        cfg.MODEL.WEIGHTS = WEIGHTS_PATH
        cfg.MODEL.DEVICE = "cpu"

        self.model = DefaultPredictor(cfg)
        self.metadata = MetadataCatalog.get(cfg.DATASETS.TEST[0])
        torch.set_grad_enabled(False)

        self.storage_client = storage.Client()

    async def process_element(
        self, input, job_id, job_args, request_id, element_index,
    ):
        # Download image
        image_bucket = job_args["input_bucket"]
        image_path = input
        with io.BytesIO() as input_buffer:
            self.storage_client.download_blob_to_file(
                f"gs://{image_bucket}/{image_path}", input_buffer
            )
            frame = np.asarray(Image.open(input_buffer))

            # RGB -> BGR
            frame_bgr = frame[:, :, ::-1]

            # Perform segmentation
            result = self.model(frame_bgr)

            # Render output
            visualizer = Visualizer(frame, self.metadata)
            vis_output = visualizer.draw_instance_predictions(
                predictions=result["instances"]
            )
            rendered = vis_output.get_image()

        # Encode image
        output = Image.fromarray(rendered)
        with io.BytesIO() as output_buffer:
            output.save(output_buffer, format="JPEG", quality=85)
            return base64.b64encode(output_buffer.getvalue()).decode("utf-8")


mapper = SegmentationMapper()
