import yaml
import os

CONFIG_PATH = "conf.yaml"

if not os.path.exists(CONFIG_PATH):
    raise FileNotFoundError(f"配置文件未找到: {CONFIG_PATH}")

with open(CONFIG_PATH, "r", encoding="utf-8") as f:
    conf = yaml.safe_load(f)

MAX_REQUESTS_PER_MINUTE = conf["rate_limit"]["max_requests_per_minute"]

CACHE_TTL_SECONDS = conf["cache"]["ttl_seconds"]
MAX_MEMORY_MB = conf["cache"]["max_memory_mb"]
MIN_MEMORY_MARGIN_MB = conf["cache"]["min_memory_margin_mb"]
MAX_DISK_CACHE_MB = conf["cache"]["max_disk_cache_mb"]
MIN_DISK_FREE_MB = conf["cache"]["min_disk_free_mb"]

IMG_DIR = conf["paths"]["img_dir"]
IMG_CACHE_DIR = conf["paths"]["img_cache_dir"]
