import asyncio
from pathlib import Path

from PIL import Image

from src.databases.s3_storage import S3Client
from src.tasks.celery_init import celery_app


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

@celery_app.task
def delete_old_pic(s3_file, bucket):
    "Удаляем старый файл из s3"
    loop = asyncio.get_event_loop()
    loop.run_until_complete(S3Client(bucket).delete_file(s3_file))

#
# import asyncio
# Пример асинхронной таски
# @celery.task
# def update_ip_user(ip):
#     loop = asyncio.get_event_loop()
#     # UserOnlineDAO.find_all() - асинхронная функция
#     items = loop.run_until_complete(UserOnlineDAO.find_all())