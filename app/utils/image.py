from PIL import Image, ImageDraw, ImageFont
import re
import os
import random
from config import IMG_DIR, IMG_CACHE_DIR

FONT_PATH = os.path.join("fonts", "ZCOOLKuaiLe-Regular.ttf")
FONT_SIZE = 20

def render_image(data: dict, image_number: int = None, cache_key: str = None, server_name: str = None, original_address: str = "") -> str:
    images = sorted(os.listdir(IMG_DIR))
    if not images:
        raise Exception("No background images found in /imgs")

    index = image_number if image_number is not None and image_number < len(images) else random.randint(0, len(images)-1)
    background = Image.open(os.path.join(IMG_DIR, images[index])).convert("RGBA")

    draw = ImageDraw.Draw(background)

    try:
        font = ImageFont.truetype(FONT_PATH, FONT_SIZE)
    except Exception as e:
        font = ImageFont.load_default()

    width, height = background.size

    title = server_name or "Minecraft服务器"
    motd = strip_color_codes(str(data.get("motd") or ""))
    host_port = original_address
    players = f"玩家: {data.get('players_online')}/{data.get('players_max')}"

    version_full = str(data.get("version_name") or "Unknown")
    version_parts = version_full.split(" ", 1)
    version_server = version_parts[0]
    version_range = version_parts[1] if len(version_parts) > 1 else ""

    status = "Online" if data.get("online", False) else "Offline"

    draw.text((20, 20), title, font=font, fill=(255, 255, 255, 255))
    draw.text((20, height//2), motd, font=font, fill=(255, 255, 255, 255))
    draw.text((20, height - 30), host_port, font=font, fill=(200, 200, 200, 255))
    draw.text((width - 220, 20), players, font=font, fill=(255, 255, 255, 255))
    draw.text((width - 220, height//2 - 20), version_server, font=font, fill=(255, 255, 255, 255))
    draw.text((width - 220, height//2), version_range, font=font, fill=(255, 255, 255, 255))
    draw.text((width - 220, height - 30), f"状态: {status}", font=font, fill=(0, 255, 0, 255) if status == "Online" else (255, 0, 0, 255))

    os.makedirs(IMG_CACHE_DIR, exist_ok=True)
    path = os.path.join(IMG_CACHE_DIR, f"{cache_key}.png")
    background.save(path)

    return path


def strip_color_codes(text):
    return re.sub(r'§[0-9a-fk-or]', '', text, flags=re.IGNORECASE)
