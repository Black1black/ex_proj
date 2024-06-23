import asyncio
from contextlib import asynccontextmanager
from datetime import datetime
from typing import List, Tuple

from aiobotocore.session import get_session
from botocore.exceptions import ClientError
from fastapi import HTTPException

from src.config import settings

# http://172.18.0.4:32827/buckets
# s3_session = aioboto3.Session(
#     aws_access_key_id=settings.MINIO_ACCESS_KEY_ID,
#     aws_secret_access_key=settings.MINIO_SECRET_ACCESS_KEY
# )
# s3_client = s3_session.client(service_name=settings.SERVICE_NAME)


class S3Client:
    def __init__(
            self,
            # access_key: str,
            # secret_key: str,
            # endpoint_url: str,
            bucket: str,
    ):
        self.config = {
            "aws_access_key_id": settings.MINIO_ACCESS_KEY_ID,
            "aws_secret_access_key": settings.MINIO_SECRET_ACCESS_KEY,
            "endpoint_url": settings.MINIO_URL, # TODO - проверить корректность работы
        }
        self.bucket = bucket
        self.session = get_session()

    @asynccontextmanager
    async def get_client(self):
        async with self.session.create_client("s3", **self.config) as client:
            yield client


    def get_s3_file_path(self, file_name: str) -> str:
        '''
        Вспомогательная функция для формирования пути к файлу в S3
        год, месяц, номер недели и день в формате текущей даты UTC
        '''
        current_date = datetime.utcnow().strftime("%Y/%m/%U/%d")

        with_timestamp = datetime.utcnow().strftime("%H_%M_%S")

        file_path = f"{current_date}/{file_name}_{with_timestamp}"
        return file_path


    async def upload_file_to_s3(self, file: bytes, s3_file: str, content_type: str):
        'Задача загрузки отдельного файла'
        try:
            async with self.get_client() as client:
                await client.put_object(Body=file, Bucket=self.bucket, Key=s3_file, ContentType=content_type)

            return f"Upload Success to {s3_file}", s3_file  # TODO - поменять имя, Возвращает сообщение об успешной загрузке и путь к файлу

        except ClientError as e:
            print(f"Error uploading file: {e}")

    async def upload_files_to_s3(self, file_group: list[tuple[bytes, str, str]]):
        'агрузка группы файлов в хранилище'
        tasks = [
            self.upload_file_to_s3(file_data, s3_file, content_type)  # Создаем задачу для загрузки каждого файла
            for file_data, s3_file, content_type in file_group
        ]

        # Ожидаем завершения всех задач загрузки
        results = await asyncio.gather(*tasks, return_exceptions=True)
    # TODO
        # Можно добавить обработку ошибок
        # Например, можно записать информацию об ошибках в лог или отправить уведомление об ошибке администратору системы.

        # Фильтруем результаты загрузки, чтобы исключить файлы, которые не были загружены успешно
        uploaded_files_paths = [s3_file for result, s3_file in results if isinstance(result, str) and result.startswith("Upload Success to ")]
        # TODO проверить работоспособность на ошибки
        return uploaded_files_paths




    async def upload_on_storage(self, user_id, files):

        MAX_FILE_SIZE = 1000000
        ALLOWED_EXTENSIONS = ('png', 'jpg', 'jpeg', 'gif', 'mp4', 'webm')  # TODO добавить форматы

        # TODO - добавить ограничения в размере в зависимости от типа файла

        file_group = []
        for _index, _file  in enumerate(files):
            if not _file.filename.lower().endswith(ALLOWED_EXTENSIONS): #(allowed_extensions):
                raise HTTPException(status_code=400, detail="Invalid file extension")

            if _file.content_type.split('/')[0] not in ['image', 'video']:
                raise HTTPException(status_code=400, detail="Invalid file type")

            if _file.filesize > MAX_FILE_SIZE:
                raise HTTPException(status_code=400, detail="File size exceeded")

            # Генерация уникального имени файла
            file_extension = _file.filename.split('.')[-1]  # Получаем расширение файла
            new_file_name = f"{user_id}_{_index}.{file_extension}"

            s3_file = self.get_s3_file_path(new_file_name)

            # Чтение содержимого файла
            content = await _file.read()

            # Добавление файла в группу для загрузки
            file_group.append((content, s3_file, _file.content_type))

        # Загрузка файлов группой
        return await self.upload_files_to_s3(file_group)



    async def delete_file(self, s3_file: str):
        try:
            async with self.get_client() as client:
                await client.delete_object(Bucket=self.bucket, Key=s3_file)
                print(f"File {s3_file} deleted from {self.bucket}")
        except ClientError as e:
            print(f"Error deleting file: {e}")


    #
    # async def get_file(self, s3_file: str, # object_name
    #                    destination_path: str):
    #     'Получение файла с s3'
    #     try:
    #         async with self.get_client() as client:
    #             response = await client.get_object(Bucket=self.bucket, Key=s3_file)
    #             data = await response["Body"].read()
    #             with open(destination_path, "wb") as file:
    #                 file.write(data)
    #             print(f"File {s3_file} downloaded to {destination_path}")
    #     except ClientError as e:
    #         print(f"Error downloading file: {e}")


#
# @app.post("/message")
# async def send_message(
#         user_id = 1,
#     text: str = Form(...),
#     files: List[UploadFile] = File(...),
#     receiver: int = Form(...),
#     publication: str = Form(...),
# ):
#     MAX_FILE_SIZE = 1000000
#     ALLOWED_EXTENSIONS = ('png', 'jpg', 'jpeg', 'gif', 'mp4', 'webm') # TODO добавить форматы
#
#
#
#
#             # return file_group
#
#     uploaded_files_paths = await upload_on_storage(user_id, files, ALLOWED_EXTENSIONS, MAX_FILE_SIZE)
#
#     save_message_to_db(text, receiver, publication)
#
#     return {"text": text, "receiver": receiver, "publication": publication, "files": uploaded_files_paths}

