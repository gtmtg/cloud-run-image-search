from detectron2.config.config import get_cfg as get_default_detectron_config

WEIGHTS_PATH = "R-50.pkl"  # model will be downloaded here during container build
RESNET_CONFIG = get_default_detectron_config()

MIN_VIZ_SCORE = 0.25
MAX_VIZ_SCORE = 0.75
