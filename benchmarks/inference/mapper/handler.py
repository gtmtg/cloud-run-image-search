import time

import numpy as np
from PIL import Image
import torch

from detectron2.layers import ShapeSpec
from detectron2.checkpoint.detection_checkpoint import DetectionCheckpointer
from detectron2.modeling.backbone.resnet import build_resnet_backbone
from detectron2.config.config import get_cfg as get_default_detectron_config

from knn.mappers import Mapper


class BenchmarkInferenceMapper(Mapper):
    def initialize_container(self, cfg, weights_path, image_path):
        # Create model
        shape = ShapeSpec(channels=3)
        self.model = torch.nn.Sequential(build_resnet_backbone(cfg, shape))

        # Load model weights
        checkpointer = DetectionCheckpointer(self.model, save_to_disk=False)
        checkpointer.load(weights_path)
        self.model.eval()
        torch.set_grad_enabled(False)

        # Store relevant attributes of config
        pixel_mean = torch.Tensor(cfg.MODEL.PIXEL_MEAN).view(-1, 1, 1)
        pixel_std = torch.Tensor(cfg.MODEL.PIXEL_STD).view(-1, 1, 1)
        self.normalize = lambda image: (image - pixel_mean) / pixel_std
        self.input_format = cfg.INPUT.FORMAT

        # Store other info
        self.image_path = image_path

    @Mapper.SkipIfError
    async def process_element(self, input, job_id, job_args, request_id, element_index):
        assert element_index == 0

        image = Image.open(self.image_path)

        # Preprocess
        assert image.mode == "RGB"
        image = torch.as_tensor(np.asarray(image), dtype=torch.float32)  # -> tensor
        image = image.permute(2, 0, 1)  # HWC -> CHW
        if self.input_format == "BGR":
            image = torch.flip(image, dims=(0,))  # RGB -> BGR
        image = image.contiguous()
        image = self.normalize(image)

        # Perform inference
        start_time = time.time()
        self.model(image.unsqueeze(dim=0))
        return time.time() - start_time


mapper = BenchmarkInferenceMapper(
    get_default_detectron_config(), "R-50.pkl", "000000003581.jpg"
)
