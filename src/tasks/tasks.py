from pathlib import Path

from src.tasks.celery_init import celery_app
from PIL import Image

@celery_app.task
def process_pic(
    path: str,
):
    im_path = Path(path)
    im = Image.open(im_path)
    for width, height in [
        (1000, 500),
        (200, 100)
    ]:
        resized_img = im.resize(size=(width, height)) # TODO - сохранять изначальные пропорции, либо обрезать фото
        resized_img.save(f"app/static/images/resized_{width}_{height}_{im_path.name}") # TODO грузить в s3

#
# import asyncio
# Пример асинхронной таски
# @celery.task
# def update_ip_user(ip):
#     loop = asyncio.get_event_loop()
#     # UserOnlineDAO.find_all() - асинхронная функция
#     items = loop.run_until_complete(UserOnlineDAO.find_all())