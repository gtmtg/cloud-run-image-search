from detectron2.config.config import get_cfg as get_default_detectron_config

WEIGHTS_CLOUD_PATH = "gs://mihir-fast-queries-west/models/R-50.pkl"
WEIGHTS_LOCAL_PATH = "tmp/models/R-50.pkl"
RESNET_CONFIG = get_default_detectron_config()
