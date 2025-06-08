from cachetools import TTLCache
from collections import OrderedDict
import os
import time
import shutil
import psutil
from config import MAX_MEMORY_MB, MIN_MEMORY_MARGIN_MB, IMG_CACHE_DIR, CACHE_TTL_SECONDS, MAX_DISK_CACHE_MB, MIN_DISK_FREE_MB
import hashlib
from urllib.parse import quote_plus
import threading

json_cache = TTLCache(maxsize=1000, ttl=600)
img_meta_cache = OrderedDict()  # {cache_key: (timestamp, img_path)}

def clear_expired_json_cache():
    json_cache.expire()

def generate_cache_key(endpoint: str, address: str, number: int = None, server_name: str = "") -> str:
    key_str = f"{endpoint}_{address}_{number or ''}_{server_name or ''}"
    return hashlib.md5(key_str.encode("utf-8")).hexdigest()

def check_memory_and_cleanup():
    mem = psutil.virtual_memory()
    available_mb = mem.available / 1024 / 1024
    
    while available_mb < MIN_MEMORY_MARGIN_MB:
        if json_cache:
            try:
                json_cache.popitem(last=False)
            except KeyError:
                pass
        elif img_meta_cache:
            try:
                _, (_, path) = img_meta_cache.popitem(last=False)
                if os.path.exists(path):
                    os.remove(path)
            except KeyError:
                pass
        
        mem = psutil.virtual_memory()
        available_mb = mem.available / 1024 / 1024
        if not json_cache and not img_meta_cache:
            break

def cache_json(key, value):
    check_memory_and_cleanup()
    json_cache[key] = value

def get_cached_json(key):
    return json_cache.get(key)

def cache_img_meta(key, image_path):
    check_memory_and_cleanup()
    img_meta_cache[key] = (time.time(), image_path)

def get_cached_img_path(key):
    return img_meta_cache.get(key, (None, None))[1]

def clear_expired_img_cache(ttl=600):
    now = time.time()
    expired_keys = [k for k, (ts, path) in img_meta_cache.items() if now - ts > ttl]
    for k in expired_keys:
        _, path = img_meta_cache[k]
        if os.path.exists(path):
            os.remove(path)
        del img_meta_cache[k]

def check_disk_space_and_cleanup():
    usage = get_directory_size_mb(IMG_CACHE_DIR)
    disk = psutil.disk_usage(IMG_CACHE_DIR)
    free_mb = disk.free / 1024 / 1024

    while usage > MAX_DISK_CACHE_MB or free_mb < MIN_DISK_FREE_MB:
        clean_oldest_image_cache()
        usage = get_directory_size_mb(IMG_CACHE_DIR)
        disk = psutil.disk_usage(IMG_CACHE_DIR)
        free_mb = disk.free / 1024 / 1024

def get_directory_size_mb(path):
    total = 0
    for dirpath, dirnames, filenames in os.walk(path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            if os.path.exists(fp):
                total += os.path.getsize(fp)
    return total / 1024 / 1024

def clean_oldest_image_cache():
    if img_meta_cache:
        key, (ts, path) = img_meta_cache.popitem(last=False)
        if os.path.exists(path):
            os.remove(path)

def background_cache_cleaner(interval_seconds=300):
    def run():
        while True:
            try:
                clear_expired_json_cache()
                clear_expired_img_cache()
                check_disk_space_and_cleanup()
                time.sleep(interval_seconds)
            except Exception as e:
                print(f"[CacheCleaner] 清理任务异常: {e}")

    t = threading.Thread(target=run, daemon=True)
    t.start()