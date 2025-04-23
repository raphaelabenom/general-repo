from minio import Minio
from minio.error import S3Error
import os
from utils import validate_bucket_name, log_error, log_info

class MinioClient:
    def __init__(self, endpoint, access_key, secret_key):
        self.endpoint = endpoint
        self.access_key = access_key
        self.secret_key = secret_key

        self.client = Minio(
            endpoint,
            access_key=access_key,
            secret_key=secret_key,
        )

    def create_bucket(self, bucket_name):
        if not validate_bucket_name(bucket_name):
            log_error(f"Invalid bucket name: {bucket_name}")
            return False

        try:
            if not self.client.bucket_exists(bucket_name):
                self.client.make_bucket(bucket_name)
                log_info(f"Bucket '{bucket_name}' created successfully.")
            else:
                log_info(f"Bucket '{bucket_name}' already exists.")
            return True
        except S3Error as err:
            log_error(f"Error creating bucket: {err}")
            return False

    def read_bucket(self, bucket_name, limit=10):
        if not validate_bucket_name(bucket_name):
            log_error(f"Invalid bucket name: {bucket_name}")
            return False

        try:
            objects = self.client.list_objects(bucket_name, recursive=True)
            stop = 0
            for obj in objects:
                log_info(f"Object: {obj.object_name}, Last Modified: {obj.last_modified}")
                stop += 1
                if stop >= limit:
                    break
            return True
        except S3Error as err:
            log_error(f"Error reading bucket: {err}")
            return False

    def delete_bucket(self, bucket_name):
        if not validate_bucket_name(bucket_name):
            log_error(f"Invalid bucket name: {bucket_name}")
            return False

        try:
            objects = self.client.list_objects(bucket_name, recursive=True)
            for obj in objects:
                self.client.remove_object(bucket_name, obj.object_name)

            self.client.remove_bucket(bucket_name)
            log_info(f"Bucket '{bucket_name}' deleted successfully.")
            return True
        except S3Error as err:
            log_error(f"Error deleting bucket: {err}")
            return False

    def update_bucket(self, old_bucket_name, new_bucket_name):
        if not validate_bucket_name(old_bucket_name) or not validate_bucket_name(new_bucket_name):
            log_error("Invalid bucket names provided.")
            return False

        try:
            if not self.client.bucket_exists(old_bucket_name):
                log_error(f"Bucket '{old_bucket_name}' does not exist.")
                return False

            if self.client.bucket_exists(new_bucket_name):
                log_error(f"Bucket '{new_bucket_name}' already exists.")
                return False

            self.create_bucket(new_bucket_name)
            objects = self.client.list_objects(old_bucket_name, recursive=True)
            for obj in objects:
                source = f"{old_bucket_name}/{obj.object_name}"
                log_info(f"Copying '{obj.object_name}' to '{new_bucket_name}'...")
                self.client.copy_object(
                    bucket_name=new_bucket_name,
                    object_name=obj.object_name,
                    source=source
                )
                self.client.remove_object(old_bucket_name, obj.object_name)

            self.delete_bucket(old_bucket_name)
            log_info(f"Bucket updated from '{old_bucket_name}' to '{new_bucket_name}'.")
            return True
        except S3Error as err:
            log_error(f"Error updating bucket: {err}")
            return False

    def upload_file(self, bucket_name, file_path, object_name):
        if not os.path.exists(file_path):
            log_error(f"File '{file_path}' does not exist.")
            return False

        if not validate_bucket_name(bucket_name):
            log_error(f"Invalid bucket name: {bucket_name}")
            return False

        try:
            self.client.fput_object(bucket_name, object_name, file_path)
            log_info(f"File '{file_path}' uploaded as '{object_name}' in bucket '{bucket_name}'.")
            return True
        except S3Error as err:
            log_error(f"Error uploading file: {err}")
            return False

    def upload_folder(self, bucket_name, folder_path):
        if not os.path.exists(folder_path) or not os.path.isdir(folder_path):
            log_error(f"Invalid folder path: {folder_path}")
            return False

        try:
            for root, dirs, files in os.walk(folder_path):
                for file in files:
                    local_file = os.path.join(root, file)
                    relative_path = os.path.relpath(local_file, folder_path).replace("\\", "/")
                    self.upload_file(bucket_name, local_file, relative_path)
            log_info("Folder upload completed successfully.")
            return True
        except Exception as err:
            log_error(f"Error uploading folder: {err}")
            return False
