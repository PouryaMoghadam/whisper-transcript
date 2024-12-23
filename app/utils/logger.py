import logging.config
import os

import yaml

from app.platform.config import Config

env = Config.ENVIRONMENT
log_level = Config.LOG_LEVEL

debug = env == "development"
# log_level = os.getenv("LOG_LEVEL", "DEBUG" if debug else "INFO").upper()


config_path = os.path.join(os.path.abspath(os.getcwd()), "uvicorn_log_conf.yaml")
with open(config_path, "r") as f:
    config = yaml.safe_load(f.read())

config["loggers"]["video-ai"]["level"] = log_level
config["loggers"]["uvicorn.error"]["level"] = log_level
config["loggers"]["uvicorn.access"]["level"] = log_level
config["root"]["level"] = log_level

logging.config.dictConfig(config)

with open(config_path, "w") as f:
    yaml.dump(config, f)

logger = logging.getLogger("video-ai")
logger.setLevel(log_level)

logger.info(f"Environment: {env}")
logger.info(f"Log level: {log_level}")
logger.debug(f"Debug messages enabled: {debug}")
